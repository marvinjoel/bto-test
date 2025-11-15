from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from src.services.clinic_service import ClinicService


class ActionCreateAppointment(Action):
    def name(self):
        return "action_create_appointment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        patient_name = tracker.get_slot("name")
        date = tracker.get_slot("date")

        service = ClinicService()
        data = {"name": patient_name, "date": date}

        try:
            response = service.create_appointment(data)

            print("📋 Respuesta de la API:", response)

            cita_id = response.get("id") or response.get("appointment_id") or "sin ID"
            dispatcher.utter_message(
                f"✅ Cita registrada para {patient_name} el {date}. ID: {cita_id}"
            )

        except Exception as e:
            dispatcher.utter_message(f"⚠️ No se pudo registrar la cita: {e}")

        return []
