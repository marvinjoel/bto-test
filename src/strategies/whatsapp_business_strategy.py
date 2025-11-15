from strategies.messaging_strategy import MessagingStrategy
from dotenv import load_dotenv

import requests
import os


load_dotenv()


class WhatsappBusinessStrategy(MessagingStrategy):

    def __init__(self) -> None:
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.api_url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, recipient: str, message: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"body": message}
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    def parse_webhook(self, request_data: dict) -> tuple[str, str]:
        if not request_data or 'entry' not in request_data:
            print("⚠️ Webhook inválido: falta 'entry'")
            return None, None

        for entry in request_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # Mensajes reales
                if 'messages' in value:
                    for msg in value.get('messages', []):
                        sender = msg.get('from', '').replace('whatsapp:', '')
                        text = msg.get('text', {}).get('body', '')
                        if sender and text:
                            return sender, text

                # Notificaciones (entregado, leído, etc.)
                elif 'statuses' in value:
                    for status in value.get('statuses', []):
                        sender = status.get('recipient_id', '')
                        if sender:
                            print(f"ℹ️ Webhook de estado ignorado para {sender}")
                            return sender, ""

        print("⚠️ No se encontró mensaje ni status válido en el webhook")
        return None, None
