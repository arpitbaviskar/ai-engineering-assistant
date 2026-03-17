# AI Engineering Assistant

A Retrieval-Augmented Generation (RAG) system for robotics and embedded systems troubleshooting.

## Features
- Semantic search over engineering knowledge
- Vector database with ChromaDB
- Local LLM reasoning with Ollama
- Robotics-focused knowledge base

## Tech Stack
Python
Sentence Transformers
ChromaDB
Ollama
FastAPI (planned)

## Architecture
User Query
→ Embedding Model
→ Vector Database
→ Retrieved Knowledge
→ LLM Reasoning
→ Engineering Answer

## Setup
pip install -r requirements.txt

## Run
python rag/build_vector_db.py
python rag/engineering_assistant.py
