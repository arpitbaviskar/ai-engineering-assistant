# backend/memory.py
from collections import defaultdict
from typing import List

# in-memory store: { session_id: [ {user, assistant}, ... ] }
_store: dict = defaultdict(list)
MAX_TURNS = 10


def get_history(session_id: str) -> List[dict]:
    return _store[session_id]


def save_turn(session_id: str, user_msg: str, assistant_msg: str):
    _store[session_id].append({
        "user": user_msg,
        "assistant": assistant_msg
    })
    if len(_store[session_id]) > MAX_TURNS:
        _store[session_id] = _store[session_id][-MAX_TURNS:]


def clear_session(session_id: str):
    _store[session_id] = []