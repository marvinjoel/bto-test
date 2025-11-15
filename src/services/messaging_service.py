from strategies.messaging_strategy import MessagingStrategy
from strategies.whatsapp_business_strategy import WhatsappBusinessStrategy

import requests
import os


RASA_WEBHOOK = os.environ.get("RASA_URL", "http://rasa_app:5005/webhooks/rest/webhook")


class MessagingService:

    def __init__(self, strategy: MessagingStrategy = None) -> None:
        self.strategy = strategy or WhatsappBusinessStrategy()

    def handle_incoming_message(self, data: dict) -> dict:
        sender, text = self.strategy.parse_webhook(data)
        if not sender or not text:
            print("⚠️ Webhook sin mensaje de texto válido. Ignorando...")
            return {"status": "ignored"}
        print(f"📩 Mensaje recibido de {sender}: {text}")
        rasa_response = requests.post(RASA_WEBHOOK, json={"sender": sender, "message": text})

        for msg in rasa_response.json():
            reply = msg.get("text")
            if reply:
                print(f"📤 Enviando respuesta a WhatsApp: {reply}")
                send_result = self.strategy.send_message(sender, reply)
                print(f"📡 Resultado envío: {send_result}")

        return {"status": "ok"}