 #core.py
# here we are using chromaDB{which is a "vector database"} and ChromaDB (the cabinet) can hold many different "collections" (drawers).
# We could have one for web pages, one for user notes, one for PDF documents, etc. and we retrive it using specific ID.
import os
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

# --- Import our new cleaning function ---
from preprocess import preprocess_transcript

# --- Setup LlamaIndex Settings ---
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = Ollama(model="gemma:2b", request_timeout=300.0)

# --- Define Paths ---
# Use relative paths that work on any OS
DB_PATH = "./vector_db"
DATA_PATH = "./data"

# --- Initialize ChromaDB ---
db = chromadb.PersistentClient(path=DB_PATH)
collection = db.get_or_create_collection("user_collection_local")
vector_store = ChromaVectorStore(chroma_collection=collection)
index = None


def generate_and_store_summary(text_content: str, doc_id: str) -> str:
    """
    Generates a summary of the provided text using the LLM
    and stores it in the Chroma collection with a specific ID.
    (Changed 'url' to 'doc_id' to be more general)
    """
    print("Generating summary...")
    prompt = f"Please provide a concise summary of the following text:\n\n{text_content}"
    
    try:
        response = Settings.llm.complete(prompt)
        summary_text = str(response)
        
        # 1. Manually embed the summary text using the LlamaIndex Setting
        print("Embedding summary using Settings.embed_model...")
        summary_embedding = Settings.embed_model.get_text_embedding(summary_text)
       
        # Use the doc_id to create a unique summary ID
        summary_id = f"summary_{doc_id}"
        
        # 2. Store the summary text AND its pre-computed embedding
        print("Upserting summary and pre-computed embedding into Chroma...")
        collection.upsert(
            documents=[summary_text],
            embeddings=[summary_embedding], 
            metadatas=[{"type": "summary", "source_doc": doc_id}],
            ids=[summary_id]
        )
        
        print(f"Summary generated and stored with ID: {summary_id}")
        return summary_text
        
    except Exception as e:
        print(f"Failed to generate or store summary: {e}")
        return ""


def process_text(raw_text: str, doc_id: str):
    """
    Takes raw (messy) text, preprocesses it, and then
    indexes it for summarization and Q&A.
    """
    
    # 1. --- CLEAN THE TEXT ---
    print(f"Preprocessing text for document: {doc_id}...")
    text = preprocess_transcript(raw_text)
    
    if not text:
        print("No text content found after preprocessing.")
        return False     
    
    # 2. --- GENERATE AND STORE SUMMARY FROM CLEANED TEXT ---
    print("Generating and storing summary...")
    generate_and_store_summary(text, doc_id)
    
    # 3. --- INDEX THE CLEANED TEXT FOR RAG ---
    print("Indexing full document for RAG...")
    os.makedirs(DATA_PATH, exist_ok=True)
    
    # Save the *cleaned* text to a file for SimpleDirectoryReader
    # This is how LlamaIndex ingests it.
    file_path = os.path.join(DATA_PATH, f"{doc_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    # Load the single cleaned text file
    docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
    
    global index
    # This indexes the *chunks* of the cleaned document
    index = VectorStoreIndex.from_documents(docs, vector_store=vector_store)
    print("Full document indexing complete.")
    
    # Clean up the temporary file
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error removing temp file: {e}")
        
    return True

def ask_question(question: str):
    """
    Asks a question to the RAG pipeline.
    """
    global index
    if not index:
        print("Reloading index from vector store...")
        # Reload from vector store if not in memory
        index = VectorStoreIndex.from_vector_store(vector_store)
        
    query_engine = index.as_query_engine()
    print(f"Querying index with question: {question}")
    resp = query_engine.query(question)
    return str(resp)

def get_summary(doc_id: str) -> str:
    """
    Retrieves a stored summary from the vector store by its unique ID.
    (Changed 'url' to 'doc_id')
    """
    summary_id = f"summary_{doc_id}"
    try:
        result = collection.get(ids=[summary_id], include=["documents"])
        
        if result and result['documents']:
            return result['documents'][0]
        else:
            return "No summary found for this ID."
            
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        return "Error finding summary."


# --- Example of how to use this file ---
if __name__ == "__main__":

    # Your messy caption sample from the preprocessor test
    sample_text_1 = """
    [Music]
    hello
    welcome<00:00:31.039><c> to</c><00:00:31.199><c> the</c><00:00:31.359><c> course</c>
    welcome to the course
    on<00:00:32.480><c> design</c><00:00:32.960><c> and</c><00:00:33.120><c> implementation</c><00:00:33.760><c> of</c><00:00:34.079><c> human</c>
    on design and implementation of human
    computer<00:00:34.880><c> interfaces</c>
    computer interfaces
    let<00:00:37.040><c> us</c><00:00:37.200><c> know</c>
    let us know
    in<00:00:38.559><c> this</c><00:00:38.800><c> course</c><00:00:39.120><c> what</c><00:00:39.360><c> we</c><00:00:39.520><c> are</c><00:00:39.600><c> going</c><00:00:39.840><c> to</c>
    in this course what we are going to
    learn
    [Music]
    """
    
    # A unique name for this document
    doc_id_1 = "hci_lecture_intro"

    # 1. Process the messy text (this will clean, summarize, and index)
    print(f"--- Processing Document: {doc_id_1} ---")
    success = process_text(sample_text_1, doc_id_1)
    
    if success:
        # 2. Ask a specific question (uses RAG on the *cleaned* text)
        print("\n" + "="*40 + "\n")
        print("--- Asking a RAG Question ---")
        question = "What is this course about?"
        answer = ask_question(question)
        print(f"Q: {question}")
        print(f"A: {answer}")

        # 3. Retrieve the summary
        print("\n" + "="*40 + "\n")
        print("--- Retrieving the Stored Summary ---")
        stored_summary = get_summary(doc_id_1)
        print(stored_summary)