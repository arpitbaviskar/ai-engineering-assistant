import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# vector database
client = chromadb.PersistentClient(path="../vector_db")

collection = client.get_collection("engineering_knowledge")


def retrieve(question, k=3):

    embedding = model.encode(question)

    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=k
    )

    return results["documents"][0]


def generate_answer(question, context):

    prompt = f"""
You are an expert robotics and embedded systems engineer.

Use the following engineering knowledge to answer the question.

Knowledge:
{context}

Question:
{question}

Provide a clear diagnosis and solution.
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    print("AI Engineering Assistant Ready\n")

    while True:

        question = input("Ask: ").strip()

        if question.lower() in ["quit", "exit"]:
            break

        docs = retrieve(question)

        context = "\n".join(docs)

        answer = generate_answer(question, context)

        print("\nAI Response:\n")

        print(answer)

        print("\n" + "-" * 50 + "\n")