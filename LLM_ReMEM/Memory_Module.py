from BCEmbedding.models.embedding import EmbeddingModel
import chromadb
from datetime import datetime
import emoji
import json
import os
import config

# init embedding model
model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1")

client = chromadb.PersistentClient(path="./chroma_db")

# with cosine similarity
collection = client.get_or_create_collection(
    name="my_collection",
    metadata={"hnsw:space": "cosine"}  
)

MEMORY_FILE = "memory.json"

# Read JSON Memory Set
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Save
def save_memory_json(memory_data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=4, ensure_ascii=False)

# Example: {'content': '中午好', 'role': 'user', 'name': 'abc}
# Change Names, Add sources, Clean Emojis, Tditting...
def input_editor(input_dict):
    # if input_dict.get('name') != None:
    #     if input_dict.get('name') == 'abc':
    #         input_dict['name'] = 'Jack'
    #     elif...

    # Remove Emoji
    def remove_emojis(text):
        return emoji.replace_emoji(text, replace='')
    
    clean_content = remove_emojis(input_dict.get('content'))
    print("emoji clean test", "\nBefore: ", input_dict.get('content'), "\nAfter: ", clean_content)
    if clean_content != '':
        input_dict['content'] = clean_content

# Embedding
def embed_text(text):
    if isinstance(text, str):
        text = [text]
    return model.encode(text)


# Add Vectors to Vector Memory Set
def Memory_saving(input_dict):
    input_editor(input_dict)

    content = input_dict.get('content').replace("\n", " ")
    name = input_dict.get('name')
    source = input_dict.get('from')
    doc_id = str(datetime.now())

    embedding = embed_text(content)
    embedding = embedding.tolist()

    memory_data = load_memory()
    memory_data[doc_id] = {
        "content": content,
        "name": input_dict.get("name", ""),  # Character Information
        "source": source
    }

    save_memory_json(memory_data)  # Save Memory in Json

    collection.add(
        documents= content,
        embeddings= embedding,
        ids= doc_id,
        metadatas={"source": source or "Unknown", "name": name or "Unknown"}
    )

# Embedding Checking and select
def Memory_checking(input_dict):
    input_editor(input_dict)
    embedding = embed_text(input_dict.get('content'))
    results = collection.query(
        query_embeddings = embedding,
        n_results=config.result_num,
        include=['documents', 'metadatas', 'distances']
    )
    return results

def get_memory_with_context(target_id, context_size):
    memory_data = load_memory()

    if not memory_data or target_id not in memory_data:
        return {"previous": [], "target": None, "next": []}

    memory_ids = list(memory_data.keys())

    index = memory_ids.index(target_id)

    prev_ids = memory_ids[max(0, index - context_size):index]
    prev_memories = [memory_data[pid] for pid in prev_ids]

    next_ids = memory_ids[index + 1: index + 1 + context_size]
    next_memories = [memory_data[nid] for nid in next_ids]

    return {
        "previous": prev_memories,
        "target": memory_data[target_id],
        "next": next_memories
    }

