from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title='TemanGalau Backend - skeleton')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post('/chat')
async def chat(req: ChatRequest):
    # TODO: replace with actual model/provider call (OpenAI, etc.) using env OPENAI_API_KEY
    user = req.message
    reply = f"Anda berkata: {user} — saya di skeleton hanya membalas dengan echo. Ganti logic ini dengan panggilan ke model AI Anda."
    return { 'reply': reply }

@app.post('/image')
async def image(prompt: dict):
    # TODO: call image generation API and return public URL
    # For skeleton return a placeholder image URL
    return { 'url': 'https://placekitten.com/512/512' }

@app.post('/speech')
async def speech(file: UploadFile = File(...)):
    # TODO: forward audio to speech-to-text service, return transcript
    # Save uploaded file temporarily
    contents = await file.read()
    size = len(contents)
    # In skeleton we just return a fake transcript
    return { 'transcript': f'(skeleton) menerima audio {file.filename} ({size} bytes)' }
