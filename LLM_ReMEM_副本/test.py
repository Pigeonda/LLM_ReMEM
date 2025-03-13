from Memory_Module import Memory_saving, Memory_checking  # 确保导入你的模块

# ✅ 测试 1：存储一条数据
print("✅ 测试 1：存储数据到 ChromaDB")
test_data = {
    "content": "李子熙26年才上大学！",
    "name": "615229654571286539",
    "from": "测试用户"
}

Memory_saving(test_data)  # 存储数据
print("数据存储完成！")

# ✅ 测试 2：查询相似数据
print("\n✅ 测试 2：查询与 '测试消息' 相似的结果")
query_data = {
    "content": "李子熙什么时候毕业",
    "name": "未知",
    "from": "未知"
}

results = Memory_checking(query_data)  # 查询数据
print("\n🔹 查询结果：", results)

mem_result = results
mem_reference = ''

mem_result = results
mem_reference = ''

# 设置相似度的筛选范围（可以修改为你的需求）
MIN_DISTANCE = -0.3  # 最小相似度
MAX_DISTANCE = 0.3  # 最大相似度

# 获取查询返回的结果数量
num_results = len(mem_result.get('ids', [[]])[0])

for i in range(num_results):  # 遍历所有返回的查询结果
    # 获取相似度
    result_distance = mem_result.get('distances', [[]])[0][i] if mem_result.get('distances') else float('inf')

    # 只筛选出相似度在 [MIN_DISTANCE, MAX_DISTANCE] 之间的结果
    if MIN_DISTANCE <= result_distance <= MAX_DISTANCE:
        # 获取时间（ID）
        result_time = mem_result.get('ids', [[]])[0][i]

        # 获取 metadata（确保不越界）
        metadata_list = mem_result.get('metadatas', [[]])[0]
        result_name = metadata_list[i].get('name', '未知') if i < len(metadata_list) else '未知'
        result_source = metadata_list[i].get('source', '未知') if i < len(metadata_list) else '未知'

        # 获取存储的文本内容
        result_content = mem_result.get('documents', [[]])[0][i] if mem_result.get('documents') else '无内容'

        # 组装参考信息
        mem_reference += (
            f"时间: {result_time}, {result_name} 在 {result_source} 说: {result_content} "
            f"(相似度: {result_distance:.3f})\n"
        )

print("✅ 处理后的参考记忆（符合相似度要求）:\n", mem_reference)

