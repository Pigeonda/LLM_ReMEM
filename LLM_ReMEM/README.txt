# LLM_ReMEM

This project is a **FastAPI-based AI memory system** that using **RAG** for vector-based storage and retrieval.  
It allows efficient memory management and enhances AI-driven responses using stored contextual information. 

More information will be updated later

*Warning: This project do not support **STREAM** yet*
---

##  Installation Guide

### 1 Clone the Repository
git clone https://github.com/Pigeonda/LLM_ReMEM.git  
cd ...\LLM_ReMEM  


### 2 Create and Activate a Virtual Environment
**macOS/Linux**  
python3 -m venv venv  
source venv/bin/activate  

**Windows**  
python -m venv venv  
venv\Scripts\activate  


### 3 Install Dependencies
pip install -r requirements.txt


### 4 Install BCEmedding
Go to the website and download (or use git)   
https://github.com/netease-youdao/BCEmbedding  
coppy the BCEmbedding file from zip  
paste it under LLM_ReMEM file  

### 5 Start the FastAPI Server First Time
uvicorn Transfer_plat:app --host 0.0.0.0 --port 8080  


### 6 Start the FastAPI Server Second Time In Terminal
**For Windows**  
cd ...\LLM_ReMEM  
venv\Scripts\activate  
uvicorn Transfer_plat:app --host 0.0.0.0 --port 8080  

**For macOS/Linux**  
cd ...\LLM_ReMEM  
source venv/bin/activate  
uvicorn Transfer_plat:app --host 0.0.0.0 --port 8080  

---
##  Instructions for use

### Config
LM_Studio_API: "http://ip:port/v1/chat/completions" # Any platforms that support OpenAI API  
*For Example, In LM Studio, the default api will be: http://127.0.0.1:1234/v1/chat/completions*  

LLM_ReMEM_API: The API of LLM_ReMEM that you are using, **Important** Changing in config will just change the log in terminal, if you want to change the port of LLM_ReMEM, please change it from start process(uvicorn Transfer_plat:app --host 0.0.0.0 --port 8080)  
*The form of using LLM_ReMEM API will be like: http://your_IPv4_ip:port/v1*  

MAIN_Model: The Model Name you are using  

temperature: Temperature for LLM  
max_tokens: Max Tokens for LLM  

MIN_DISTANCE = -0.1  # Smallest Similarity, Don't need to Change usually  
MAX_DISTANCE = 0.5  # Maximum Similarity, if larger than this will be ignore  

context_size: The size of how many context will be get from target message  
result_num: The number of how many message will be drawn from embedding check  

prompt: the system prompt for LLM, the memory will be appended after your prompt, notice that you must write prompt here, if you write in other place, it will be overwrite by prompt from here.

### input_editor (Function In Memory_Module)
It does include a basic function of remove all emojis in text.  
It do have other functions that can setting by yourself.  
This part is been showing in the code:  
![image](https://github.com/user-attachments/assets/e3e9848a-be13-4b22-9126-fb53c7f0bff5)  

In Example, you can see there is a role and name in given dict. Usually when role is user, it is you, you can change the name to your name, like this:  

![image](https://github.com/user-attachments/assets/d7f84e28-4e7d-49cb-aa19-00dcff851a56)  

In this case, we have been changed name to Jack, simillarly, we can chagne source by other condition:

![image](https://github.com/user-attachments/assets/9dae89f9-629b-413b-9dfc-09e525bb9260)  

**What can we do with that?**
1. In Memory_Module:
   There is a function Memory_saving(input_dict), the name and source can be added in metadatas, also you can add any other metadata by yourself  

![image](https://github.com/user-attachments/assets/fc9b2e01-f554-493a-baf1-0a788a9b2c4a)  

2. In Transfer_plat:  
   ![image](https://github.com/user-attachments/assets/82eb2e7a-b565-4fc0-8795-fbcf11c17cba)  

   Under function async chat_completions(request: OpenAIChatRequest, background_tasks: BackgroundTasks), assume that context_size is 1 and result_num is 2,the output of prompt will be like:  
   Related Memory 1:  
   time, Jack on Discord said: ...  
   time, Jack on Discord said: ...  
   time, Jack on Discord said: ...  
   Related Memory 2:  
   time, Jack on Discord said: ...  
   time, Jack on Discord said: ...  
   time, Jack on Discord said: ...  
  
   The Jack here, is name, and the Discord is source, you can change them to other metadatas or the way to output.

---
## Flow Chat  
![image](https://github.com/user-attachments/assets/3dc0b96f-bc4a-4265-8af4-0480ae822509)
