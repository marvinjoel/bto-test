import os
import requests

class ClinicService:
    def __init__(self):
        self.base_url = os.getenv("CLINIC_API_URL")
        self.api_key = os.getenv("CLINIC_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_patient_info(self, patient_id: str) -> dict:
        url = f"{self.base_url}/patients/{patient_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_appointment(self, data: dict) -> dict:
        url = f"{self.base_url}/appointments"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
