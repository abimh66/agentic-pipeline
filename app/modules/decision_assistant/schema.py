from pydantic import BaseModel


class CreateDecisionJob(BaseModel):
    topic: str
