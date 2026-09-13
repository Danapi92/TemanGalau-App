from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import jwt
import time
from typing import Optional

# OpenAI usage
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo')

JWT_SECRET = os.getenv('JWT_SECRET', 'replace_this_secret')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
JWT_EXP_SECONDS = int(os.getenv('JWT_EXP_SECONDS', '3600'))

if not OPENAI_API_KEY:
    print('Warning: OPENAI_API_KEY not set. /chat, /image, /speech will return skeleton responses unless set.')

app = FastAPI(title='TemanGalau Backend - OpenAI integrated (skeleton)')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class IDTokenRequest(BaseModel):
    id_token: str

async def verify_jwt_token(auth_header: Optional[str] = Header(None)):
    if not auth_header:
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    scheme, _, token = auth_header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail='Invalid auth scheme')
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.post('/auth/google')
async def auth_google(req: IDTokenRequest):
    id_token = req.id_token
    if not id_token:
        raise HTTPException(status_code=400, detail='id_token required')
    # Verify with Google's tokeninfo endpoint
    resp = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': id_token})
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Invalid Google ID token')
    info = resp.json()
    # Optional: verify audience if GOOGLE_CLIENT_ID is set
    if GOOGLE_CLIENT_ID and info.get('aud') != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail='ID token audience mismatch')
    # Create our own JWT for session
    now = int(time.time())
    payload = {
        'sub': info.get('sub'),
        'email': info.get('email'),
        'name': info.get('name'),
        'iat': now,
        'exp': now + JWT_EXP_SECONDS,
    }
    access_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return { 'access_token': access_token, 'token_type': 'bearer' }

@app.post('/chat')
async def chat(req: ChatRequest, user=Depends(verify_jwt_token)):
    user_msg = req.message
    if not OPENAI_API_KEY:
        # fallback skeleton response
        reply = f"(skeleton) Anda berkata: {user_msg} — set OPENAI_API_KEY untuk jawaban nyata."
        return { 'reply': reply }

    try:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': OPENAI_CHAT_MODEL,
            'messages': [
                {'role': 'system', 'content': 'You are a friendly, supportive virtual companion in Indonesian.'},
                {'role': 'user', 'content': user_msg}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # compatible with Chat Completions response
        choices = data.get('choices') or []
        if len(choices) > 0:
            content = choices[0].get('message', {}).get('content') or choices[0].get('text')
        else:
            content = '(OpenAI returned no choices)'
        reply = content
        return {'reply': reply}
    except Exception as e:
        # Log and return fallback
        print('OpenAI chat error', e)
        raise HTTPException(status_code=500, detail='OpenAI chat error')

@app.post('/image')
async def image(prompt: dict, user=Depends(verify_jwt_token)):
    prompt_text = prompt.get('prompt') if isinstance(prompt, dict) else None
    if not prompt_text:
        prompt_text = 'a friendly companion portrait, soft lighting, anime style'

    if not OPENAI_API_KEY:
        return { 'url': 'https://placekitten.com/512/512' }

    try:
        url = 'https://api.openai.com/v1/images/generations'
        headers = { 'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json' }
        payload = { 'prompt': prompt_text, 'n': 1, 'size': '512x512' }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # new Images API may return data[0].url
        img_url = None
        if data.get('data') and len(data['data']) > 0:
            img_url = data['data'][0].get('url') or data['data'][0].get('b64_json')
        if img_url and img_url.startswith('data:'):
            # if b64 data returned, we can't host it; return as-is
            return {'url': img_url}
        if not img_url:
            # fallback
            img_url = 'https://placekitten.com/512/512'
        return {'url': img_url}
    except Exception as e:
        print('OpenAI image error', e)
        raise HTTPException(status_code=500, detail='OpenAI image error')

@app.post('/speech')
async def speech(file: UploadFile = File(...), user=Depends(verify_jwt_token)):
    contents = await file.read()
    size = len(contents)
    if not OPENAI_API_KEY:
        return { 'transcript': f'(skeleton) menerima audio {file.filename} ({size} bytes) - user {user.get("email")}' }

    try:
        # Use OpenAI Whisper transcription endpoint
        url = 'https://api.openai.com/v1/audio/transcriptions'
        headers = { 'Authorization': f'Bearer {OPENAI_API_KEY}' }
        files = {
            'file': (file.filename, contents, file.content_type or 'audio/wav')
        }
        data = { 'model': 'whisper-1' }
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        transcript = result.get('text') or result.get('transcript')
        # Optionally generate an automatic reply using the chat endpoint
        reply = None
        try:
            # call our own chat to generate a response to the transcript
            chat_resp = requests.post(
                'http://127.0.0.1:8000/chat',
                headers={'Authorization': f'Bearer {jwt.encode({"sub": user.get("sub")}, JWT_SECRET, algorithm="HS256")}', 'Content-Type': 'application/json'},
                json={'message': transcript},
                timeout=20
            )
            if chat_resp.status_code == 200:
                reply = chat_resp.json().get('reply')
        except Exception:
            reply = None

        return { 'transcript': transcript, 'reply': reply }
    except Exception as e:
        print('OpenAI speech error', e)
        raise HTTPException(status_code=500, detail='OpenAI speech error')
