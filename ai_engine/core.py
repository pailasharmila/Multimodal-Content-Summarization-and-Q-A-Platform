#core.py
#here we are using chromaDB{which is a "vector database"} and ChromaDB (the cabinet) can hold many different "collections" (drawers).
#  We could have one for web pages, one for user notes, one for PDF documents, etc. and we retrive it using specific ID.
import os, requests, chromadb
from bs4 import BeautifulSoup
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="gemma:2b", request_timeout=300.0)

db = chromadb.PersistentClient(path="./vector_db")
collection = db.get_or_create_collection("user_collection_local")
vector_store = ChromaVectorStore(chroma_collection=collection)
index = None

def fetch_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            s.decompose()
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n\n".join(p for p in paragraphs if p)
    except Exception as e:
        print(f"Fetch failed: {e}")
        return ""


def generate_and_store_summary(text_content: str, url: str) -> str:
    """
    Generates a summary of the provided text using the LLM
    and stores it in the Chroma collection with a specific ID.
    """
    print("Generating summary...")
    prompt = f"Please provide a concise summary of the following text:\n\n{text_content}"
    
    try:
        response = Settings.llm.complete(prompt)
        summary_text = str(response)
        
        # --- START OF FIX ---
        # 1. Manually embed the summary text using the LlamaIndex Setting
        print("Embedding summary using Settings.embed_model...")
        summary_embedding = Settings.embed_model.get_text_embedding(summary_text)
       

        summary_id = f"summary_{url}"
        
        # 2. Store the summary text AND its pre-computed embedding
    
        print("Upserting summary and pre-computed embedding into Chroma...")
        collection.upsert(
            documents=[summary_text],
            embeddings=[summary_embedding], # <--- PASS THE EMBEDDING HERE
            metadatas=[{"type": "summary", "source_url": url}],
            ids=[summary_id]
        )
        
        print(f"Summary generated and stored with ID: {summary_id}")
        return summary_text
        
    except Exception as e:
        print(f"Failed to generate or store summary: {e}")
        return ""


def process_url(url: str):
    text = fetch_text_from_url(url)
    if not text:
        return False     
    print("Generating and storing summary...")
    generate_and_store_summary(text, url)
    print("Indexing full document for RAG...")
    os.makedirs("/data", exist_ok=True)
    file_path = os.path.join("/data", "page.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    docs = SimpleDirectoryReader("/data").load_data()
    
    global index
    # This indexes the *chunks* of the full document using the correct model
    index = VectorStoreIndex.from_documents(docs, vector_store=vector_store)
    print("Full document indexing complete.")
    return True

def ask_question(question: str):
    global index
    if not index:
        print("Reloading index from vector store...")
        index = VectorStoreIndex.from_vector_store(vector_store)
        
    query_engine = index.as_query_engine()
    resp = query_engine.query(question)
    return str(resp)

def get_summary(url: str) -> str:
    """
    Retrieves a stored summary from the vector store by its unique ID.
    """
    summary_id = f"summary_{url}"
    try:
        result = collection.get(ids=[summary_id], include=["documents"])
        
        if result and result['documents']:
            return result['documents'][0]
        else:
            return "No summary found for this URL."
            
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        return "Error finding summary."

# --- Example of how to use it (No changes) ---
if __name__ == "__main__":
    # 1. Process a URL (this will scrape, summarize, and index)
    test_url = "https://www.ultipa.com/docs/graph-analytics-algorithms/skip-gram"
    print(f"Processing URL: {test_url}")
    success = process_url(test_url)
    
    if success:
        # 2. Ask a specific question (uses RAG on the full text)
        print("\n--- Asking a RAG Question ---")
        question = "What is Skip-gram?"
        answer = ask_question(question)
        print(f"Q: {question}")
        print(f"A: {answer}")

        # 3. Retrieve the summary (uses the new get_summary function)
        print("\n--- Retrieving the Stored Summary ---")
        stored_summary = get_summary(test_url)
        print(stored_summary)