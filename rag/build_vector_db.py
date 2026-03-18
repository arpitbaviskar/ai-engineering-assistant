import os
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# absolute paths — work from any directory
BASE_DIR = r"E:\ai_engineering_robotics_assistant_architecture"
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
collection = client.get_or_create_collection("engineering_knowledge")

total_chunks = 0

for filename in os.listdir(KNOWLEDGE_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(KNOWLEDGE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    file_chunks = 0

    for chunk in chunks:
        chunk_id = str(hash(chunk))
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue

        embedding = model.encode(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding.tolist()],
            ids=[chunk_id],
            metadatas=[{"source": filename}]
        )
        file_chunks += 1
        total_chunks += 1

    print(f"  {filename}: {file_chunks} new chunks added")

print(f"\nDone. {total_chunks} new chunks embedded.")
print(f"Total in DB: {collection.count()}")