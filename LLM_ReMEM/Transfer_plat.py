from fastapi import FastAPI, HTTPException, BackgroundTasks
import logging
import time
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import requests
import config
from Memory_Module import Memory_saving, Memory_checking, get_memory_with_context

app = FastAPI()

# LM Studio 服务器地址
LM_STUDIO_API_URL = config.LM_Studio_API

# 你的两个 LLM（一个用于记忆处理，一个用于语言输出）
MEM_Model = config.MEMMORY_Model  # 记忆处理模型
LLM_Model = config.MAIN_Model     # 语言处理模型

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Now FastAPI Platform is valid on ")

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    # 不再考虑流式，直接移除或保留都行，这里保留但无效
    stream: Optional[bool] = False

def query_lm_studio(model_name, messages, temperature, max_tokens):
    """
    只做一次性返回的查询，不再支持流式。
    """
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False  # 强制取消流式
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(LM_STUDIO_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        if "choices" not in json_response:
            raise ValueError(f"❌ API 响应错误: {json_response}")

        # 只拿一次性完整内容
        return json_response["choices"][0]["message"]["content"]

    except requests.RequestException as e:
        logging.error(f"❌ LM Studio 模型 {model_name} 处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as ve:
        logging.error(f"❌ API 返回错误: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))

@app.post("/v1/chat/completions")
async def chat_completions(request: OpenAIChatRequest, background_tasks: BackgroundTasks):
    """OpenAI 兼容的 /v1/chat/completions 端点，只能一次性整块返回。"""

    logging.info("🔹 收到新请求，开始记忆处理...")
    logging.info(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if request.messages:
        logging.info(f"📥 用户输入: {request.messages[-1].get('content', '')}")

    # ========= 记忆处理 ===========
    last_user_msg = None
    # 从后往前找，找到第一条 role=="user" 的消息
    for msg in reversed(request.messages):
        if msg["role"] == "user":
            last_user_msg = msg
            break

    if not last_user_msg:
        logging.warning("没有发现用户消息，跳过 MEM 处理。")
        mem_reference = ""
    else:
        mem_result = Memory_checking(last_user_msg)
        mem_reference = ""
        mem_distance = ""
        mem_count = 1

        # 2) 读取相似度范围配置
        MIN_DISTANCE = config.MIN_DISTANCE
        MAX_DISTANCE = config.MAX_DISTANCE

        # 3) 取出 IDs，用于后续循环
        ids_list = mem_result.get("ids", [[]])[0]
        distances_list = mem_result.get("distances", [[]])[0]
        metadatas_list = mem_result.get("metadatas", [[]])[0]

        num_results = len(ids_list)

        # 4) 遍历所有检索到的记忆
        for i in range(num_results):
            # 获取相似度
            result_distance = distances_list[i] if i < len(distances_list) else float("inf")

            # 根据相似度范围过滤
            if MIN_DISTANCE <= result_distance <= MAX_DISTANCE:
                result_time = ids_list[i]
                # 获取元数据
                md = metadatas_list[i] if i < len(metadatas_list) else {}
                result_name = md.get("name", "未知")
                result_source = md.get("source", "未知")

                # 通过 get_memory_with_context() 获取上下文
                memory_context = get_memory_with_context(result_time, config.context_size)
                previous_context = memory_context.get("previous", [])
                target_content = memory_context.get("target", {}).get("content", "未知内容")
                next_context = memory_context.get("next", [])

                # 去掉毫秒
                result_time_to_sec = result_time.split(".")[0]

                # 拼接输出
                mem_reference += f"\n相关记忆 {mem_count}:\n"
                mem_count += 1

                # 前文
                for prev in previous_context:
                    name_prev = prev.get("name", "未知")
                    src_prev = prev.get("source", "未知")
                    cnt_prev = prev.get("content", "")
                    mem_reference += f"{result_time_to_sec}，{name_prev} 在 {src_prev} 说：{cnt_prev}\n"

                # 目标
                mem_reference += f"{result_time_to_sec}，{result_name} 在 {result_source} 说：{target_content}\n"

                # 后文
                for nxt in next_context:
                    name_nxt = nxt.get("name", "未知")
                    src_nxt = nxt.get("source", "未知")
                    cnt_nxt = nxt.get("content", "")
                    mem_reference += f"{result_time_to_sec}，{name_nxt} 在 {src_nxt} 说：{cnt_nxt}\n"

                # 记录相似度
                mem_distance += f"(相似度: {result_distance:.3f})\n"

        # 如果为空说明没有符合相似度的记忆
        if not mem_reference:
            mem_reference = "无相关记忆"

    logging.info(f"MEM输出:\n{mem_reference}")
    logging.info(f"MEM最相关记忆距离:\n{mem_distance}")

    # 把 MEM 输出合并到 system 提示
    system_msg = None
    for msg in request.messages:
        if msg["role"] == "system":
            system_msg = msg
            break

    if system_msg is None:
        system_msg = {"role": "system", "content": ""}
        request.messages.insert(0, system_msg)

    system_msg["content"] = config.prompt + f"\n（参考记忆：{mem_reference}）"

    # 调用 LLM，非流式
    lm_response = query_lm_studio(
        model_name=LLM_Model,
        messages=request.messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens
    )

    logging.info(f"📤 LLM模型回复: {lm_response}")

    # 一次性返回完整回答
    response_data = {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": LLM_Model,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": lm_response
                },
                "finish_reason": "stop"
            }
        ]
    }

        # **在后台存储记忆**
    if last_user_msg:
        background_tasks.add_task(Memory_saving, last_user_msg)
        background_tasks.add_task(Memory_saving, {
            "content": lm_response, "role": "assistant", "name": "霓露", "from": ""
        })

    return response_data

