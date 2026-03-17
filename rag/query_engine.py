import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="../vector_db")

collection = client.get_collection("engineering_knowledge")


def search_knowledge(question, n=3):

    embedding = model.encode(question)

    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=n,
        include=["documents", "distances"]
    )

    docs = results["documents"][0]
    scores = results["distances"][0]

    return list(zip(docs, scores))


if __name__ == "__main__":

    print("System ready (offline retrieval mode)\n")

    while True:

        question = input("Ask: ").strip()

        if question.lower() in ["quit", "exit"]:
            break

        pairs = search_knowledge(question)

        if not pairs:
            print("No relevant knowledge found.\n")
            continue

        print(f"\nTop {len(pairs)} results for: '{question}'\n")

        for i, (doc, score) in enumerate(pairs, 1):

            similarity = max(0, 1 - score)

            print(f"[{i}] similarity={similarity:.3f}")

            preview = doc.replace("\n", " ")

            print(preview[:300] + ("..." if len(preview) > 300 else ""))

            print()