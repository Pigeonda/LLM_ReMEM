LM_Studio_API = "http://your_ip/v1/chat/completions" # Any platforms that support OpenAI API
LLM_ReMEM_API = "http://0.0.0.0:8080/v1"  # Notice that Changing from here will not work

MAIN_Model = ""

temperature = 0.8
max_tokens = 512

MIN_DISTANCE = -0.1  # Smallest Similarity, Don't need to Change usually
MAX_DISTANCE = 0.5  # Maximum Similarity, if larger than this will be ignore

context_size = 2  # The size of how many context will be get from target message
result_num = 3  # The number of how many message will be drawn from embedding check

prompt = (
    '''
    
    '''
    )