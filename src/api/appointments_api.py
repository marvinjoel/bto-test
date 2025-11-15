from fastapi import APIRouter

router = APIRouter()

@router.post("")
def create_appointment(data: dict) -> dict:

    return {"message": "Cita registrada correctamente", "data": data}
