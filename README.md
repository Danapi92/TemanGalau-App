# TemanGalau-App — Android (Expo) skeleton

A minimal skeleton for an Android-only AI companion app using Expo (React Native) for the frontend and FastAPI for a small backend forwarding requests to AI/image/speech providers.

This branch contains a starter app so anyone can run and test locally. It uses environment variables for API keys.

Quick start (local):

1) Frontend
- cd frontend
- npm install
- expo start
- Run on Android device/emulator via Expo Go or a standalone build.

2) Backend
- cd backend
- python -m venv .venv
- source .venv/bin/activate  # or .venv\Scripts\activate on Windows
- pip install -r requirements.txt
- Copy .env.example -> .env and fill keys (OPENAI_API_KEY or other provider keys)
- uvicorn main:app --reload --host 0.0.0.0 --port 8000

Notes
- The frontend expects BACKEND_URL in frontend/.env or edit the constant in App.js to point to your backend (e.g., http://10.0.2.2:8000 for Android emulator, or http://192.168.x.y:8000 for device)
- This is a skeleton: replace forwarding logic in backend/main.py with your provider-specific code.

Files added:
- frontend/ (Expo app)
- backend/ (FastAPI app)
- .gitignore
- .env.example

License: MIT
