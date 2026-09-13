I updated the skeleton to add Google Sign-In and simple session tokens.

What I changed:
- Frontend: added Google auth flow (expo-auth-session) and local storage of app access token; sign in/out UI; frontend now sends Authorization header to backend when available.
- Backend: added /auth/google to exchange Google ID token for a backend-signed JWT (requires JWT_SECRET); endpoints /chat, /image, /speech now require Authorization: Bearer <token>.
- requirements.txt updated for pyjwt and requests.

Next steps for you to run this locally:
1) Configure environment
- Copy .env.example -> .env and set GOOGLE_CLIENT_ID and JWT_SECRET (and OPENAI_API_KEY later if integrating).
2) Frontend
- In frontend/package.json we've added dependencies. Install them with npm install.
- Replace GOOGLE_CLIENT_ID in frontend/App.js with the Android client ID from Google Cloud Console, or configure properly for your Expo environment.
3) Backend
- Install backend requirements and run uvicorn as before.

Security notes
- JWT_SECRET must be a strong random secret in production.
- For production Android builds, configure proper OAuth client IDs and redirect URIs in Google Cloud Console. The current setup is a skeleton for local/dev testing.

If you want, I can now:
- Integrate OpenAI for /chat and image generation.
- Wire up a real speech-to-text provider for /speech.
- Create a PR from init/app-skeleton into main when ready.
