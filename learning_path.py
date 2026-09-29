from config import GEMINI_API_KEY, GEMINI_MODEL, is_configured, logger
import requests


def get_learning_recommendations(topic: str) -> str:
    if not is_configured():
        return "Gemini API key is not configured. Add your GEMINI_API_KEY in the .env file."

    prompt = (
        f"Recommend a clear learning path for '{topic}'. Include beginner, intermediate, and advanced steps, "
        "plus practical study activities and resources."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 700},
    }

    try:
        response = requests.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload, timeout=60)
        if response.status_code in {404, 429, 500, 502, 503, 504} and GEMINI_MODEL != "gemini-3.1-flash-lite":
            fallback_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
            logger.warning(
                "Gemini model %s returned HTTP %d; retrying learning recommendations with gemini-3.1-flash-lite",
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
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        return text.strip() if text else "Unable to generate recommendations right now."
    except Exception as exc:
        logger.exception("Gemini learning recommendation failed")
        return f"Error generating recommendations: {exc}"
