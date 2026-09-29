from config import GEMINI_API_KEY, GEMINI_MODEL, is_configured, logger
import requests


def summarize_text(text: str) -> str:
    if not is_configured():
        return "Gemini API key is not configured. Add your GEMINI_API_KEY in the .env file."

    prompt = (
        "Summarize the following text in a concise and readable way while keeping the most important points.\n\n"
        f"{text}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
    }

    try:
        response = requests.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload, timeout=60)
        if response.status_code in {429, 500, 502, 503, 504}:
            logger.warning(
                "Gemini model %s returned HTTP %d; retrying summarization",
                GEMINI_MODEL,
                response.status_code,
            )
            response = requests.post(url, headers={"x-goog-api-key": GEMINI_API_KEY}, json=payload, timeout=60)
        if response.status_code in {404, 429, 500, 502, 503, 504} and GEMINI_MODEL != "gemini-3.1-flash-lite":
            fallback_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
            logger.warning(
                "Gemini model %s returned HTTP %d; retrying summarization with gemini-3.1-flash-lite",
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
        summary = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        return summary.strip() if summary else "Unable to summarize the text right now."
    except Exception as exc:
        logger.exception("Gemini summarization failed")
        return f"Error summarizing text: {exc}"
