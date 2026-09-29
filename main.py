"""
main.py
-------
EduGenie: Google Gemini Powered Learning Assistant
FastAPI backend entry point.

Endpoints (as documented):
  GET  /qa                      - Q&A
  POST /explain/                - Concept explanation
  POST /summarize/               - Summarization
  POST /quiz                    - Quiz generation
  GET  /learn/recommendations   - Personalized learning path

Also serves the HTML+CSS frontend at "/".
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations
from config import is_configured, logger

app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --------------------------------------------------------------------------
# Frontend
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# --------------------------------------------------------------------------
# Health check (handy for verifying the API key / server status quickly)
# --------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": is_configured(),
    }


# --------------------------------------------------------------------------
# Q&A - GET API using Gemini
# --------------------------------------------------------------------------
@app.get("/qa")
async def answer_question(question: str = Query(...)):
    answer = answer_question_with_gemini(question)
    return {"answer": answer}


# --------------------------------------------------------------------------
# Explanation - POST API
# --------------------------------------------------------------------------
@app.post("/explain/")
async def explain_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body. Please send {\"topic\": \"...\"}."}, status_code=400)

    topic = data.get("topic") if isinstance(data, dict) else None
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    explanation = explain_topic(topic)
    return {"topic": topic, "explanation": explanation}


# --------------------------------------------------------------------------
# Summarization - POST API
# --------------------------------------------------------------------------
@app.post("/summarize/")
async def summarize_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body. Please send {\"text\": \"...\"}."}, status_code=400)

    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)
    summary = summarize_text(text)
    return {"summary": summary}


# --------------------------------------------------------------------------
# Quiz Generation - POST API
# --------------------------------------------------------------------------
@app.post("/quiz")
async def quiz_api(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body. Please send {\"text\": \"...\"}."}, status_code=400)

    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)
    quiz = generate_quiz(text)
    logger.info("Generated quiz with %d item(s)", len(quiz) if isinstance(quiz, list) else 0)
    return JSONResponse(content={"quiz": quiz})


# --------------------------------------------------------------------------
# Learning Recommendations - GET API
# --------------------------------------------------------------------------
@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str = Query(...)):
    recommendation = get_learning_recommendations(topic)
    return {"topic": topic, "recommendation": recommendation}


if __name__ == "__main__":
    import os
    import socket

    import uvicorn

    def get_available_port(start_port: int, max_tries: int = 20) -> int:
        for port in range(start_port, start_port + max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"No available port found starting from {start_port}")

    host = os.getenv("HOST", "127.0.0.1")
    requested_port = int(os.getenv("PORT", "8010"))
    port = get_available_port(requested_port)
    uvicorn.run("main:app", host=host, port=port, reload=True)