from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import jwt
import time
from typing import Optional

JWT_SECRET = os.getenv('JWT_SECRET', 'replace_this_secret')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
JWT_EXP_SECONDS = int(os.getenv('JWT_EXP_SECONDS', '3600'))

app = FastAPI(title='TemanGalau Backend - skeleton with Google Auth')

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
    # TODO: replace with actual model/provider call (OpenAI, etc.) using env OPENAI_API_KEY
    user_msg = req.message
    reply = f"Anda berkata: {user_msg} — (skeleton response). Authenticated as {user.get('email')}."
    return { 'reply': reply }

@app.post('/image')
async def image(prompt: dict, user=Depends(verify_jwt_token)):
    # TODO: call image generation API and return public URL
    return { 'url': 'https://placekitten.com/512/512' }

@app.post('/speech')
async def speech(file: UploadFile = File(...), user=Depends(verify_jwt_token)):
    # TODO: forward audio to speech-to-text service, return transcript
    contents = await file.read()
    size = len(contents)
    return { 'transcript': f'(skeleton) menerima audio {file.filename} ({size} bytes) - user {user.get("email")}' }
