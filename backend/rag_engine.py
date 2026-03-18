import chromadb, requests, os
from sentence_transformers import SentenceTransformer
import ollama

# absolute path — works no matter where uvicorn is launched from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_db")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma = chromadb.PersistentClient(path=r"E:\ai_engineering_robotics_assistant_architecture\vector_db")

# use get_or_create so it never crashes if collection is missing
collection = chroma.get_or_create_collection("engineering_knowledge")
CONFIDENCE_THRESHOLD = 0.5


def retrieve(question: str, n: int = 3):
    emb = embed_model.encode(question)
    res = collection.query(
        query_embeddings=[emb.tolist()],
        n_results=n,
        include=["documents", "distances", "metadatas"]
    )
    docs   = res["documents"][0]
    dists  = res["distances"][0]
    sources = [m.get("source", "unknown") for m in res["metadatas"][0]]
    return docs, dists[0], sources


def web_search(question: str):
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": question + " robotics",
                    "format": "json", "no_html": 1},
            timeout=5
        )
        data = r.json()
        results = []
        if data.get("AbstractText"):
            results.append(data["AbstractText"])
        for t in data.get("RelatedTopics", [])[:3]:
            if isinstance(t, dict) and t.get("Text"):
                results.append(t["Text"])
        return results
    except:
        return []


def generate_answer(question: str, history: list = None):
    docs, best_dist, sources = retrieve(question)
    local_ctx = "\n---\n".join(docs)

    # web fallback if local confidence low
    web_ctx = ""
    if best_dist > CONFIDENCE_THRESHOLD:
        web_results = web_search(question)
        web_ctx = "\n".join(web_results)

    # build conversation history string
    history_str = ""
    if history:
        for turn in history[-4:]:  # last 4 turns only
            history_str += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"

    prompt = f"""You are an expert robotics and electronics engineer.
Use the knowledge base and web results to answer accurately.

KNOWLEDGE BASE:
{local_ctx}

{"WEB RESULTS:" + web_ctx if web_ctx else ""}

{"CONVERSATION HISTORY:" + history_str if history_str else ""}

QUESTION: {question}

Give a structured answer: identify causes, explain why, provide fixes."""

    try:
        resp = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp["message"]["content"], sources
    except Exception as e:
        return f"Error generating answer: {str(e)}", sources