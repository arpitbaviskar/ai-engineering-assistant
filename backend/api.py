from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid, sys

# add backend/ folder to path so sibling imports work
sys.path.insert(0, os.path.dirname(__file__))

from models import (Query, Answer, MemoryQuery, MemoryAnswer,
                    CodeRequest, CodeResponse, VisionResponse)
from rag_engine import generate_answer
from memory import get_history, save_turn
from code_generator import generate_code
from vision_service import analyze_image

app = FastAPI(title="AI Engineering Assistant", version="1.0")

# allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "AI Engineering Assistant running"}


# ── 1. Basic RAG Q&A ──────────────────────────────
@app.post("/ask", response_model=Answer)
def ask(q: Query):
    answer, sources = generate_answer(q.question)
    return Answer(question=q.question, answer=answer, sources=sources)


# ── 2. RAG with conversation memory ───────────────
@app.post("/ask/memory", response_model=MemoryAnswer)
def ask_with_memory(q: MemoryQuery):
    history = get_history(q.session_id)
    answer, _ = generate_answer(q.question, history=history)
    save_turn(q.session_id, q.question, answer)
    return MemoryAnswer(
        session_id=q.session_id,
        question=q.question,
        answer=answer,
        history_length=len(get_history(q.session_id))
    )


# ── 3. Robotics code generation ───────────────────
@app.post("/generate", response_model=CodeResponse)
def generate(req: CodeRequest):
    code = generate_code(req.robot, req.controller,
                          req.task, req.language)
    return CodeResponse(robot=req.robot, controller=req.controller,
                          task=req.task, code=code)


# ── 4. Vision diagnostics ─────────────────────────
@app.post("/vision", response_model=VisionResponse)
async def vision(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    tmp = f"tmp_{uuid.uuid4().hex}.jpg"
    with open(tmp, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        result = analyze_image(tmp)
    finally:
        os.remove(tmp)
    return result