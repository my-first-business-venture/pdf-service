import json
import asyncio
import httpx
import logging

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List

from config import OPENAI_KEY, LLM_MODEL
from services.pdf_loader import load_pdf_content
from services.vector_index import LlamaIndexService

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App & Middleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global vars
CONVERSATION_HISTORY: Dict[str, List[Dict[str, str]]] = {}
llama_index_service: Optional[LlamaIndexService] = None

# Prompt
EXPERT_PROMPT = """
You are a helpful assistant and an expert in accessible travel for individuals with disabilities. You answer questions strictly based on the following PDF content:

{context}

Important: If the answer is not contained in the document, respond that you don't know.

Answer in a concise and clear manner.
"""

# Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"

# Startup
@app.on_event("startup")
async def startup_event():
    global llama_index_service
    logger.info("🔄 Loading PDF...")
    pdf_text = load_pdf_content()
    logger.info("✅ PDF loaded")
    llama_index_service = LlamaIndexService(pdf_text)
    logger.info("✅ LlamaIndex initialized")

# Stream Chat
async def stream_chat_response(user_message: str, conversation_id: str):
    history = CONVERSATION_HISTORY.setdefault(conversation_id, [])
    history.append({"role": "user", "content": user_message})

    # Get relevant content
    filtered_context = llama_index_service.get_relevant_context(user_message)
    prompt_text = EXPERT_PROMPT.format(context=filtered_context)

    messages = [{"role": "system", "content": prompt_text}] + history

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            openai_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                },
            )
            data = openai_response.json()
            logger.debug(f"data: {data}")
            final_content = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}")
            final_content = "An error occurred while processing your request."

    history.append({"role": "assistant", "content": final_content})
    yield f"data: {json.dumps({'type': 'content', 'content': final_content})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

# Endpoints
@app.post("/chat")
async def chat_endpoint(body: ChatRequest):
    return StreamingResponse(
        stream_chat_response(body.message, body.conversation_id),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    async def health_stream():
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'status': 'ok'})}\n\n"
    return StreamingResponse(health_stream(), media_type="text/event-stream")
