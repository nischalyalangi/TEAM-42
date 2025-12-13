import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# --- Configuration (Must match data_processor.py) ---
INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "text_chunks.pkl"
MODEL_NAME = 'all-MiniLM-L6-v2' 
K = 5 # Default number of top results to retrieve

class RAGRetriever:
    """
    A class to handle loading the FAISS index and performing vector search 
    to retrieve relevant text chunks for a given query.
    """
    def __init__(self):
        self.index = None
        self.text_chunks = None
        self.model = None
        self.is_ready = False
        self._load_components()

    def _load_components(self):
        """Loads the FAISS index, text chunks, and the Sentence Transformer model."""
        
        print("--- RAG Retriever: Loading Components ---")
        
        # 1. Load FAISS Index
        if not os.path.exists(INDEX_FILE):
            print(f"ERROR: FAISS index file '{INDEX_FILE}' not found. Please run data_processor.py first.")
            return

        try:
            self.index = faiss.read_index(INDEX_FILE)
            print(f"Loaded FAISS index with {self.index.ntotal} vectors.")
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return

        # 2. Load Text Chunks
        if not os.path.exists(CHUNKS_FILE):
            print(f"ERROR: Text chunks file '{CHUNKS_FILE}' not found. Please run data_processor.py first.")
            return

        try:
            with open(CHUNKS_FILE, 'rb') as f:
                self.text_chunks = pickle.load(f)
            print(f"Loaded {len(self.text_chunks)} text chunks.")
        except Exception as e:
            print(f"Error loading text chunks: {e}")
            return

        # 3. Load Embedding Model
        try:
            self.model = SentenceTransformer(MODEL_NAME)
            self.is_ready = True
            print("Retriever is initialized and ready.")
        except Exception as e:
            print(f"Error loading Sentence Transformer model: {e}")
            self.is_ready = False


    def retrieve_context(self, query: str, k: int = K) -> list[str]:
        """
        Takes a user query and finds the top-k most relevant text chunks.
        """
        if not self.is_ready:
            print("Retriever is not ready. Aborting retrieval.")
            return []

        # 1. Convert the query into a vector (embedding)
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        query_embedding = np.array([query_embedding]).astype('float32') # FAISS requires a 2D array

        # 2. Perform the FAISS search: D=distances, I=indices
        D, I = self.index.search(query_embedding, k)
        
        # 3. Get the corresponding text chunks
        top_k_indices = I[0]
        # Filter indices to ensure they are within the bounds of text_chunks list
        retrieved_chunks = [self.text_chunks[idx] for idx in top_k_indices if 0 <= idx < len(self.text_chunks)]

        return retrieved_chunks


if __name__ == "__main__":
    # Example Test: This requires the index files to exist!
    retriever = RAGRetriever()
    
    if retriever.is_ready:
        test_query = "What is the difference between Batch Normalization and Layer Normalization?"
        print(f"\nSearching for context related to: '{test_query}'")
        
        context = retriever.retrieve_context(test_query, k=3)
        
        print("\n--- Retrieved Context Chunks (Top 3) ---")
        for i, chunk in enumerate(context):
            print(f"Chunk {i+1}:\n{chunk}\n{'='*30}")