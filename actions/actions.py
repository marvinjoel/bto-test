import os
import requests
import logging

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from datetime import datetime

logger = logging.getLogger(__name__)
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://python_app:8000/api")

class ActionCreateAppointment(Action):
    def name(self):
        return "action_create_appointment"

    def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("name")
        date_text = tracker.get_slot("date")

        # Convertir fecha a formato YYYY-MM-DD
        try:
            date_of_attention = self.convert_date(date_text)
        except Exception as e:
            dispatcher.utter_message(
                "Lo siento, no pude entender la fecha. ¿Podrías indicarla nuevamente?"
            )
            return []

        # Cargar valores estáticos desde variables de entorno
        payload = {
            "doctor_id": int(os.getenv("CLINIC_DOCTOR_ID")),
            "speciality_id": int(os.getenv("CLINIC_SPECIALITY_ID")),
            "customer_id": int(os.getenv("CLINIC_CUSTOMER_ID")),
            "schedule_id": int(os.getenv("CLINIC_SCHEDULE_ID")),
            "schedule_detail_id": int(os.getenv("CLINIC_SCHEDULE_DETAIL_ID")),
            "establishment_id": int(os.getenv("CLINIC_ESTABLISHMENT_ID")),
            "date_of_attention": date_of_attention,
            "hour_of_attention": "09:00:00",
            "state_admission_id": os.getenv("CLINIC_STATE_ADMISSION_ID")
        }

        api_url = os.getenv("CLINIC_API_URL")
        api_key = os.getenv("CLINIC_API_KEY")

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "x-api-key": api_key
        }

        try:
            response = requests.post(f"{api_url}/appointments", json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                dispatcher.utter_message(
                    f"Perfecto {name}, tu cita ha sido registrada para el {date_of_attention}."
                )
            else:
                dispatcher.utter_message(
                    "⚠️ Lo siento, no pude completar la reserva. Inténtalo más tarde."
                )
                print("Error:", response.text)

        except Exception as e:
            dispatcher.utter_message(
                "⚠️ Lo siento, no pude comunicarme con el servicio de citas. Inténtalo más tarde."
            )
            print("Exception:", e)

        # limpiar slots
        return [SlotSet("name", None), SlotSet("date", None)]

    def convert_date(self, text):
        import re
        text = text.lower().strip()

        # Mapa de meses
        months = {
            "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
            "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
            "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
        }

        # 1️⃣ Formato exacto: 25/11/2025
        try:
            return datetime.strptime(text, "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            pass

        # 2️⃣ Formato exacto: 25-11-2025
        try:
            return datetime.strptime(text, "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            pass

        # 3️⃣ Formato: "25 de noviembre"
        match = re.match(r"(\d{1,2})\s*de\s*(\w+)", text)
        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            if month_name in months:
                month = months[month_name]
                year = datetime.now().year
                return f"{year}-{month}-{day:02d}"

        # 4️⃣ Formato: "martes 25" → usa mes actual
        dias = [
            "lunes", "martes", "miercoles", "miércoles",
            "jueves", "viernes", "sabado", "sábado", "domingo"
        ]

        if any(d in text for d in dias):
            number = re.findall(r"\d+", text)
            if number:
                day = int(number[0])
                now = datetime.now()
                return f"{now.year}-{now.month:02d}-{day:02d}"

        # 5️⃣ "el próximo lunes"
        if "próximo" in text or "proximo" in text:
            # EXTRA: si quieres lo implementamos
            pass

        raise ValueError("No pude convertir la fecha")