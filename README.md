# EduGenie AI

FastAPI learning assistant with Gemini-powered Q&A, explanations, summaries, quizzes, and learning paths.

## Deploy to Render

1. Push this project to a GitHub repository. The `.gitignore` excludes `.env` and Python virtual environments; do not commit API keys.
2. In Render, choose **New** > **Blueprint** and connect the GitHub repository containing `render.yaml`.
3. Enter your Gemini API key when Render prompts for `GEMINI_API_KEY`, then deploy.
4. Use the stable `onrender.com` URL assigned to the service. Free services may sleep when idle; choose a paid plan if you need it to remain continuously available.

The API key belongs in Render's environment settings, not in `render.yaml` or the repository. The local `.env` file continues to be used for development.