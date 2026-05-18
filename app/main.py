from scalar_fastapi import get_scalar_api_reference
from app.core.settings import settings
from fastapi import FastAPI
from app.modules.decision_assistant.router import decision_assitant_router

app = FastAPI(title=settings.app_name)

app.include_router(decision_assitant_router)


@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
