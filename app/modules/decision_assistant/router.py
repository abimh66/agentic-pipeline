from app.modules.decision_assistant.tasks import start_process
from fastapi import APIRouter, status
from app.modules.decision_assistant.schema import CreateDecisionJob

decision_assitant_router = APIRouter(
    prefix="/api/decision-assistant", tags=["Decision Assitant"]
)


@decision_assitant_router.post("/", status_code=status.HTTP_202_ACCEPTED)
def start_tasks(payload: CreateDecisionJob):
    start_process.delay(payload.topic)

    return {"message": "Job in-process!"}
