from config import GEMINI_API_KEY, GEMINI_MODEL, is_configured, logger
import requests


def explain_topic(topic: str) -> str:
    if not is_configured():
        return "Gemini API key is not configured. Add your GEMINI_API_KEY in the .env file."

    prompt = (
        f"Explain the topic '{topic}' in simple, educational language. "
        "Break it into clear sections: what it is, why it matters, and a short example."
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
                "Gemini model %s returned HTTP %d; retrying explanation with gemini-3.1-flash-lite",
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
        return text.strip() if text else "Unable to explain this topic right now."
    except Exception as exc:
        logger.exception("Gemini explanation failed")
        return f"Error explaining topic: {exc}"
