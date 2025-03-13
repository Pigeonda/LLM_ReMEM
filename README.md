# LLM_ReMEM

# LLM_ReMEM

This project is a **FastAPI-based AI memory system** that utilizes **ChromaDB** for vector-based storage and retrieval.
It allows efficient memory management and enhances AI-driven responses using stored contextual information.

---

##  Installation Guide

### 1 Clone the Repository
git clone https://github.com/Pigeonda/LLM_ReMEM.git
cd LLM_ReMEM


### 2 Create and Activate a Virtual Environment
macOS/Linux
python3 -m venv venv
source venv/bin/activate

Windows
python -m venv venv
venv\Scripts\activate


### 3 Install Dependencies
pip install -r requirements.txt


### 4 Install BCEmedding
Go to the website and download (or use git) 
https://github.com/netease-youdao/BCEmbedding
coppy the BCEmbedding file from zip
paste it under LLM_ReMEM file

### 5 Start the FastAPI Server
uvicorn Transfer_plat:app --host 0.0.0.0 --port 8080
