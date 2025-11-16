from fastapi import APIRouter, HTTPException
from requests import RequestException
from services.clinic_service import ClinicService
from fastapi.params import Body

router = APIRouter()

@router.post("")
def create_appointment_endpoint(data: dict = Body(...)):
    """
    Endpoint para crear una cita, consumido por Rasa Action Server.
    """
    patient_name = data.get("name")
    date = data.get("date")

    if not patient_name or not date:
        raise HTTPException(status_code=400, detail="Name and date are required")

    service = ClinicService()
    service_data = {"name": patient_name, "date": date}

    try:
        response = service.create_appointment(service_data)
        print("📋 Respuesta de la API externa:", response)
        return response

    except RequestException as e:
        if e.response is not None:
            raise HTTPException(status_code=e.response.status_code,
                                detail=f"Error from Clinic API: {e.response.text}")
        else:
            raise HTTPException(status_code=503,
                                detail=f"Clinic API unreachable: {e}")
