Update: I integrated OpenAI endpoints into the backend skeleton for chat, image generation, and speech-to-text (Whisper).

What I changed:
- backend/main.py now calls OpenAI REST APIs when OPENAI_API_KEY is set:
  - /chat -> Chat Completions (gpt-3.5-turbo by default)
  - /image -> Images Generations
  - /speech -> Audio Transcriptions (whisper-1)
- backend/requirements.txt added openai and requests (requests used for REST calls).

How to configure (required)
1) Set OPENAI_API_KEY in backend/.env (copy from .env.example). If you don't set it, endpoints will return skeleton/placeholders.
2) Keep GOOGLE_CLIENT_ID and JWT_SECRET populated for Google auth to work.

Notes & limitations
- The current implementation uses blocking requests (requests library) inside FastAPI endpoints. For production or high throughput, switch to an async HTTP client (httpx) or OpenAI official async client and run calls off the event loop.
- The /speech endpoint uploads user audio to OpenAI for transcription — ensure you are comfortable sending audio to OpenAI and follow privacy/regulatory constraints.
- The /speech handler attempts to call the local /chat endpoint to generate an automatic reply; this uses a local call and a short-lived JWT and may need hardening.

Next steps I can do for you
- Replace blocking requests with httpx async calls.
- Add rate-limiting per user to prevent abuse (recommended) and to enforce usage quotas.
- Add storage for conversation history (SQLite/Postgres) and billing/usage tracking.

If you want me to proceed with any of the next steps, tell me which one and I'll implement it next on branch init/app-skeleton.
