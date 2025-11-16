import os
import requests

class ClinicService:
    def __init__(self):
        self.base_url = os.getenv("CLINIC_API_URL")
        self.api_key = os.getenv("CLINIC_API_KEY")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_patient_info(self, patient_id: str) -> dict:
        url = f"{self.base_url}/patients/{patient_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_appointment(self, data: dict) -> dict:
        """
        data = {
          "name": "Joel Sanchez",
          "date": "2025-11-25"
        }
        """

        # Convertir fecha que viene de Rasa
        date_of_attention = data["date"]

        # Construir payload REAL para API
        payload = {
            "doctor_id": int(os.getenv("CLINIC_DOCTOR_ID")),
            "speciality_id": int(os.getenv("CLINIC_SPECIALITY_ID")),
            "customer_id": int(os.getenv("CLINIC_CUSTOMER_ID")),
            "schedule_id": int(os.getenv("CLINIC_SCHEDULE_ID")),
            "schedule_detail_id": int(os.getenv("CLINIC_SCHEDULE_DETAIL_ID")),
            "establishment_id": int(os.getenv("CLINIC_ESTABLISHMENT_ID")),
            "date_of_attention": date_of_attention,
            "hour_of_attention": "09:00:00",
            "state_admission_id": os.getenv("CLINIC_STATE_ADMISSION_ID"),
        }

        url = f"{self.base_url}/appointments"
        print("📤 Enviando a API externa:", payload)

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        print("📥 Respuesta API externa:", response.text)

        response.raise_for_status()
        return response.json()