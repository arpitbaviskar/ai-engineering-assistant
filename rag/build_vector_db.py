import os
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="../vector_db")
collection = client.get_or_create_collection("engineering_knowledge")

knowledge_dir = "../knowledge"
total_chunks = 0

for filename in os.listdir(knowledge_dir):
    if not filename.endswith(".txt"):
        continue  # skip non-txt files

    filepath = os.path.join(knowledge_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # split into paragraphs (blank line = new chunk)
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    file_chunks = 0

    for chunk in chunks:
        chunk_id = str(hash(chunk))
        # check if already embedded — skip duplicates
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue

        embedding = model.encode(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding.tolist()],
            ids=[chunk_id],
            metadatas=[{"source": filename}]  # track which file
        )
        file_chunks += 1
        total_chunks += 1

    print(f"  {filename}: {file_chunks} new chunks added")

print(f"\nDone. {total_chunks} new chunks embedded.")
print(f"Total in DB: {collection.count()}")