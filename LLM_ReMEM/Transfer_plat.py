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

LM_STUDIO_API_URL = config.LM_Studio_API

LLM_Model = config.MAIN_Model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Now FastAPI Platform is valid on {0}".format(config.LLM_ReMEM_API))

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False

def query_lm_studio(model_name, messages, temperature, max_tokens):
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(LM_STUDIO_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        if "choices" not in json_response:
            raise ValueError(f"API error: {json_response}")

        return json_response["choices"][0]["message"]["content"]

    except requests.RequestException as e:
        logging.error(f"Model {model_name} processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as ve:
        logging.error(f"API return error: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))

@app.post("/v1/chat/completions")
async def chat_completions(request: OpenAIChatRequest, background_tasks: BackgroundTasks):

    logging.info("Request recieved")
    logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if request.messages:
        logging.info(f"User Input: {request.messages[-1].get('content', '')}")

    # ========= Memory Processing ===========
    last_user_msg = None
    # Find the first user msg
    for msg in reversed(request.messages):
        if msg["role"] == "user":
            last_user_msg = msg
            break

    if not last_user_msg:
        logging.warning("No message finded, memory process will be skip")
        mem_reference = ""
    else:
        mem_result = Memory_checking(last_user_msg)
        mem_reference = ""
        mem_distance = ""
        mem_count = 1

        # Similarity range
        MIN_DISTANCE = config.MIN_DISTANCE
        MAX_DISTANCE = config.MAX_DISTANCE

        ids_list = mem_result.get("ids", [[]])[0]
        distances_list = mem_result.get("distances", [[]])[0]
        metadatas_list = mem_result.get("metadatas", [[]])[0]

        num_results = len(ids_list)

        for i in range(num_results):
            result_distance = distances_list[i] if i < len(distances_list) else float("inf")

            if MIN_DISTANCE <= result_distance <= MAX_DISTANCE:
                result_time = ids_list[i]

                md = metadatas_list[i] if i < len(metadatas_list) else {}
                result_name = md.get("name", "Unknown")
                result_source = md.get("source", "Unknown")

                memory_context = get_memory_with_context(result_time, config.context_size)
                previous_context = memory_context.get("previous", [])
                target_content = memory_context.get("target", {}).get("content", "Unknown")
                next_context = memory_context.get("next", [])

                # delet ms
                result_time_to_sec = result_time.split(".")[0]

                mem_reference += f"\nRelated Memory {mem_count}:\n"
                mem_count += 1

                for prev in previous_context:
                    name_prev = prev.get("name", "Unknown")
                    src_prev = prev.get("source", "Unknown")
                    cnt_prev = prev.get("content", "")
                    mem_reference += f"{result_time_to_sec},{name_prev} on {src_prev} said: {cnt_prev}\n"

                mem_reference += f"{result_time_to_sec},{result_name} on {result_source} said: {target_content}\n"

                for nxt in next_context:
                    name_nxt = nxt.get("name", "Unknown")
                    src_nxt = nxt.get("source", "Unknown")
                    cnt_nxt = nxt.get("content", "")
                    mem_reference += f"{result_time_to_sec}，{name_nxt} 在 {src_nxt} 说：{cnt_nxt}\n"

                # Record Similarity
                mem_distance += f"(Similarity: {result_distance:.3f})\n"

        if not mem_reference:
            mem_reference = "No memory finded"

    logging.info(f"MEM output:\n{mem_reference}")
    logging.info(f"MEM distance:\n{mem_distance}")

    # Add Memory to the end of System Prompt
    system_msg = None
    for msg in request.messages:
        if msg["role"] == "system":
            system_msg = msg
            break

    if system_msg is None:
        system_msg = {"role": "system", "content": ""}
        request.messages.insert(0, system_msg)

    system_msg["content"] = config.prompt + f"\n(Memory:{mem_reference})"

    lm_response = query_lm_studio(
        model_name=LLM_Model,
        messages=request.messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens
    )

    logging.info(f"Return: {lm_response}")

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

        # Memory Saving
    if last_user_msg:
        background_tasks.add_task(Memory_saving, last_user_msg)
        background_tasks.add_task(Memory_saving, {
            "content": lm_response, "role": "assistant", "name": "", "from": ""
        })

    return response_data

