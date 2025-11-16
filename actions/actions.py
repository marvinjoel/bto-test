import os
import requests
import logging

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://python_app:8000/api")

class ActionCreateAppointment(Action):
    def name(self):
        return "action_create_appointment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        patient_name = tracker.get_slot("name")
        date = tracker.get_slot("date")
        endpoint = f"{BACKEND_URL}/appointments"
        data = {"name": patient_name, "date": date}

        try:
            response = requests.post(endpoint, json=data, timeout=10)
            response.raise_for_status()

            response_data = response.json()
            cita_id = response_data.get("id") or response_data.get("appointment_id", "sin ID")

            dispatcher.utter_message(
                f"✅ Cita registrada para {patient_name} el {date}. ID: {cita_id}"
            )

        except RequestException as e:
            logger.error(f"Error calling internal backend: {e}")
            if e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", e.response.text)
                except:
                    error_detail = e.response.text
                dispatcher.utter_message(template="utter_api_error_reason", error_reason=error_detail)
            else:
                dispatcher.utter_message(template="utter_api_error")

        return []