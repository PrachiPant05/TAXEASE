import os
import pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)

index = pinecone.Index("tax-assistant-index")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Add a document to the index
def add_to_index(doc_id, text, metadata=None):
    vector = encoder.encode([text])[0].tolist()
    index.upsert([(doc_id, vector, metadata or {})])

# Search for similar documents
def search_similar(query, top_k=3):
    vector = encoder.encode([query])[0].tolist()
    result = index.query(vector=vector, top_k=top_k, include_metadata=True)
    return result.matches
