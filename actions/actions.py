import os
import requests
import logging

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from datetime import datetime

logger = logging.getLogger(__name__)
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://python_app:8000/api")


class ActionCheckAvailability(Action):
    def name(self):
        return "action_check_availability"

    def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("name")
        date_text = tracker.get_slot("date")

        # Convertir fecha
        try:
            date_of_attention = self.convert_date(date_text)
        except Exception:
            dispatcher.utter_message("Lo siento, no pude entender la fecha. ¿Puedes repetirla?")
            return []

        # Llamar API availability
        api_url = os.getenv("CLINIC_API_URL")
        api_key = os.getenv("CLINIC_API_KEY")

        doctor_id = int(os.getenv("CLINIC_DOCTOR_ID"))
        speciality_id = int(os.getenv("CLINIC_SPECIALITY_ID"))

        url = (
            f"{api_url}/schedules/availability"
            f"?doctorId={doctor_id}&specialityId={speciality_id}"
            f"&startDate={date_of_attention}&endDate={date_of_attention}"
        )

        headers = {"x-api-key": api_key, "accept": "application/json"}

        logger.info(f"Consultando horarios: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if not data["data"]:
                dispatcher.utter_message(
                    f"Lo siento {name}, no hay horarios disponibles el {date_of_attention}. "
                    "¿Quieres escoger otra fecha?"
                )
                return []

            # Extraer horas
            hours = [item["start_time"] for item in data["data"]]

            # Mostrar horas al usuario
            dispatcher.utter_message(
                f"Perfecto {name}, estos son los horarios disponibles para el {date_of_attention}:"
            )

            msg = "\n".join([f"• {h}" for h in hours])
            dispatcher.utter_message(msg)

            dispatcher.utter_message("¿Cuál horario deseas reservar?")

            return [
                SlotSet("converted_date", date_of_attention),
                SlotSet("available_hours", hours)
            ]

        except Exception as e:
            logger.exception(f"Error consultando horarios: {e}")
            dispatcher.utter_message("Lo siento, no pude obtener los horarios disponibles.")
            return []


class ActionCreateAppointment(Action):
    def name(self):
        return "action_create_appointment"

    def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("name")
        chosen_hour = tracker.get_slot("hour")
        date_of_attention = tracker.get_slot("converted_date")

        if not chosen_hour:
            dispatcher.utter_message("Por favor indícame qué horario deseas reservar.")
            return []

        # Construir payload usando HORA SELECCIONADA
        payload = {
            "doctor_id": int(os.getenv("CLINIC_DOCTOR_ID")),
            "speciality_id": int(os.getenv("CLINIC_SPECIALITY_ID")),
            "customer_id": int(os.getenv("CLINIC_CUSTOMER_ID")),
            "schedule_id": int(os.getenv("CLINIC_SCHEDULE_ID")),
            "schedule_detail_id": int(os.getenv("CLINIC_SCHEDULE_DETAIL_ID")),
            "establishment_id": int(os.getenv("CLINIC_ESTABLISHMENT_ID")),
            "date_of_attention": date_of_attention,
            "hour_of_attention": f"{chosen_hour}:00",
            "state_admission_id": str(os.getenv("CLINIC_STATE_ADMISSION_ID"))
        }

        api_url = os.getenv("CLINIC_API_URL")
        api_key = os.getenv("CLINIC_API_KEY")

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "x-api-key": api_key
        }

        try:
            response = requests.post(f"{api_url}/appointments", json=payload, headers=headers)

            logger.info(f"Payload enviado: {payload}")
            logger.info(f"Respuesta: {response.text}")

            if response.status_code in [200, 201]:
                dispatcher.utter_message(
                    f"Perfecto {name}, tu cita ha sido registrada para el {date_of_attention} a las {chosen_hour}."
                )
            else:
                dispatcher.utter_message("Lo siento, no pude completar la reserva.")
        except Exception as e:
            logger.exception(f"Error creando cita: {e}")
            dispatcher.utter_message("Hubo un problema con el servidor, intenta más tarde.")

        # Limpiar
        return [
            SlotSet("name", None),
            SlotSet("date", None),
            SlotSet("hour", None),
            SlotSet("available_hours", None),
            SlotSet("converted_date", None)
        ]

    def convert_date(self, text):
        import re
        text = text.lower().strip()

        months = {
            "septiembre": "09",
            "setiembre": "09",
            "sep": "09"
        }

        # 1) DD/MM/YYYY
        try:
            return datetime.strptime(text, "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            pass

        try:
            return datetime.strptime(text, "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            pass

        # 3) "3 de septiembre"
        match = re.match(r"(\d{1,2})\s*(de\s*)?(\w+)", text)
        if match:
            day = int(match.group(1))
            month_name = match.group(3)
            if month_name in months:
                return f"2025-{months[month_name]}-{day:02d}"

        # -------------------------
        # 3) Formato: "sábado 6" / "sabado 6" / "martes 3"
        # -------------------------
        dias = [
            "lunes", "martes", "miercoles", "miércoles",
            "jueves", "viernes", "sabado", "sábado", "domingo"
        ]
        if any(d in text for d in dias):
            numbers = re.findall(r"\d+", text)
            if numbers:
                day = int(numbers[0])
                # POR AHORA todo septiembre, como tú pediste
                return f"2025-09-{day:02d}"

        raise ValueError("No pude convertir la fecha")