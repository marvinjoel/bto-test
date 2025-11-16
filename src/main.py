from fastapi import FastAPI
from api import whatsapp_api, appointments_api

app = FastAPI(title="Chatbot Clínica API")

# Routers
app.include_router(whatsapp_api.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(appointments_api.router, prefix="/api/appointments", tags=["Appointments"])

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
