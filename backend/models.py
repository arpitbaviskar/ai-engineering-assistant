from pydantic import BaseModel
from typing import Optional, List


# ── /ask ──────────────────────────────────────────
class Query(BaseModel):
    question: str


class Answer(BaseModel):
    question: str
    answer: str
    sources: List[str] = []


# ── /ask/memory ───────────────────────────────────
class MemoryQuery(BaseModel):
    session_id: str          # unique ID per conversation
    question: str


class MemoryAnswer(BaseModel):
    session_id: str
    question: str
    answer: str
    history_length: int


# ── /generate ─────────────────────────────────────
class CodeRequest(BaseModel):
    robot: str               # e.g. "4 DOF arm"
    controller: str          # e.g. "Arduino Uno"
    task: str                # e.g. "rotate base servo to 90 degrees"
    language: Optional[str] = "Arduino C++"


class CodeResponse(BaseModel):
    robot: str
    controller: str
    task: str
    code: str


# ── /vision ───────────────────────────────────────
class VisionResponse(BaseModel):
    detections: List[dict]
    diagnosis: str