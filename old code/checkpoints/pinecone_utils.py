# pinecone_utils.py
import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
load_dotenv()

# Load API keys
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")  # Not used in v3

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

INDEX_NAME = "comedy-sketch-index"
DIMENSIONS = 1536

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSIONS,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Update if needed
    )

index = pc.Index(INDEX_NAME)

# --- Get embedding from OpenAI ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

# --- Store script embedding ---
def embed_and_store_script(script_text: str, metadata: dict = None):
    embedding = get_embedding(script_text)
    index.upsert(vectors=[{
        "id": "script-001",
        "values": embedding,
        "metadata": metadata or {"source": "reference", "text": script_text}
    }])
    print("✅ Script successfully embedded to Pinecone!")

# --- Retrieve closest script ---
def fetch_reference_script(query_text: str) -> str:
    query_embedding = get_embedding(query_text)
    result = index.query(vector=query_embedding, top_k=1, include_metadata=True)
    return result["matches"][0]["metadata"].get("text", "")
