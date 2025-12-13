import os
import pickle
import faiss
import numpy as np
import tiktoken
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# --- Configuration ---
SOURCE_FILE = "Machine-learning-all-topics.txt"
INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "text_chunks.pkl"
MODEL_NAME = 'all-MiniLM-L6-v2' # A highly efficient, small, and powerful embedding model
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# --- Helper Function for Token-based Text Splitting ---
def split_text_into_chunks(text: str, model_name: str, chunk_size: int, chunk_overlap: int):
    """Splits a long text into chunks using tiktoken for precise token control."""
    try:
        # Use tiktoken for tokenization (mimics common LLM tokenization)
        encoding = tiktoken.get_encoding("cl100k_base") # General-purpose encoding for modern models
        tokens = encoding.encode(text)
        
        chunks = []
        for i in range(0, len(tokens), chunk_size - chunk_overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    except Exception as e:
        print(f"Error during text splitting: {e}")
        return []

# --- Main Processing Logic ---
def process_data():
    """Loads text, chunks it, embeds it, and builds a FAISS index."""
    print(f"--- 1. Loading data from {SOURCE_FILE} ---")
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: Source file '{SOURCE_FILE}' not found. Please create it in your project folder.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    print("--- 2. Splitting text into chunks (using tiktoken) ---")
    text_chunks = split_text_into_chunks(full_text, "cl100k_base", CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"Generated {len(text_chunks)} text chunks.")

    print(f"--- 3. Loading Sentence Transformer model: {MODEL_NAME} ---")
    # This automatically downloads the model if not cached
    model = SentenceTransformer(MODEL_NAME)
    
    print("--- 4. Generating embeddings and building FAISS index ---")
    
    # Generate embeddings for all text chunks (using tqdm for progress bar)
    embeddings = model.encode(text_chunks, show_progress_bar=True, convert_to_numpy=True)
    
    # Ensure the embeddings are float32, which is required by FAISS
    embeddings = np.array(embeddings).astype('float32')

    # Get the dimension of the vectors (e.g., all-MiniLM-L6-v2 produces 384 dimensions)
    d = embeddings.shape[1] 

    # Create a FAISS index: IndexFlatL2 is a simple Euclidean distance (L2 norm) index
    index = faiss.IndexFlatL2(d)
    
    # Add the vectors to the index
    index.add(embeddings)

    print(f"FAISS index created with {index.ntotal} vectors of dimension {d}.")

    print("--- 5. Saving index and text chunks to disk ---")
    
    # Save the FAISS index
    faiss.write_index(index, INDEX_FILE)
    
    # Save the corresponding text chunks using pickle
    with open(CHUNKS_FILE, 'wb') as f:
        pickle.dump(text_chunks, f)

    print("\n✅ Data processing complete.")
    print(f"   - Index saved to: {INDEX_FILE}")
    print(f"   - Chunks saved to: {CHUNKS_FILE}")

if __name__ == "__main__":
    process_data()