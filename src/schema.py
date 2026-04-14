"""Action schema definition using Pydantic.

Defines the ActionSchema data model for validated action generation.
"""

from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class ActionSchema(BaseModel):
    """Schema for generated actions.

    Attributes:
        action: Name of the action/tool to execute.
        parameters: Parameters for the specific action.
        risk_level: Safety level of the action.
    """

    action: str = Field(description="The name of the action/tool to execute")
    parameters: Dict[str, Any] = Field(
        description="The parameters for the specific action"
    )
    risk_level: Literal["safe", "medium", "dangerous"] = Field(
        description="The risk level associated with this action"
    )
