from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    action: str = Field(..., description="The name of the action to perform")
    parameters: dict = Field(..., description="Dictionary of parameters for the action")
