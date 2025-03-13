LM_Studio_API = "http://192.168.2.1:1234/v1/chat/completions"
LLM_ReMEM_API = "http://0.0.0.0:8080/v1"

MAIN_Model = "gemma-2-27b-it@q8_0"

temperature = 0.8
max_tokens = 512

MIN_DISTANCE = -0.1  # 最小相似度
MAX_DISTANCE = 0.5  # 最大相似度

context_size = 2
result_num = 3

prompt = (
    '''
    
    '''
    )