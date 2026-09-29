import json
import re

from config import GEMINI_API_KEY, GEMINI_MODEL, is_configured, logger
import requests


def generate_quiz(text: str):
    if not is_configured():
        return [{"question": "Gemini API key is not configured.", "options": ["Please add your GEMINI_API_KEY in .env"], "answer": "Please add your GEMINI_API_KEY in .env"}]

    prompt = (
        "Generate a quiz from the following text. Return valid JSON in this exact format: "
        "[{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"...\"}, ...]. "
        "Create 5 multiple-choice questions.\n\n"
        f"{text}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1200},
    }

    try:
        response = requests.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload, timeout=60)
        if response.status_code in {429, 500, 502, 503, 504}:
            logger.warning(
                "Gemini model %s returned HTTP %d; retrying quiz request",
                GEMINI_MODEL,
                response.status_code,
            )
            response = requests.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload, timeout=60)
        if response.status_code in {404, 429, 500, 502, 503, 504} and GEMINI_MODEL != "gemini-3.1-flash-lite":
            fallback_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
            logger.warning(
                "Gemini model %s returned HTTP %d; retrying quiz with gemini-3.1-flash-lite",
                GEMINI_MODEL,
                response.status_code,
            )
            response = requests.post(
                fallback_url,
                headers={"x-goog-api-key": GEMINI_API_KEY},
                json=payload,
                timeout=60,
            )
        response.raise_for_status()
        data = response.json()
        result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        if not result:
            return []

        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        quiz = json.loads(cleaned)
        if isinstance(quiz, list):
            return quiz
        return []
    except Exception as exc:
        logger.exception("Gemini quiz generation failed")
        return [{"question": f"Error generating quiz: {exc}", "options": ["Try again later"], "answer": "Try again later"}]
