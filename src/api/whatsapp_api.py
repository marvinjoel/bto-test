from fastapi import APIRouter, Request, Query, Response, HTTPException
from services.messaging_service import MessagingService

import os

router = APIRouter()
service = MessagingService()
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    return service.handle_incoming_message(body)