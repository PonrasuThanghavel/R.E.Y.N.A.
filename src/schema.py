from typing import Any, Dict, Literal
from pydantic import BaseModel, Field


class ActionSchema(BaseModel):
    action: str = Field(description="The name of the action/tool to execute")
    parameters: Dict[str, Any] = Field(
        description="The parameters for the specific action"
    )
    risk_level: Literal["safe", "medium", "dangerous"] = Field(
        description="The risk level associated with this action"
    )
