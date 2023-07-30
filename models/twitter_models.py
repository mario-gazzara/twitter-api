from typing import List

from pydantic import BaseModel


class EmptyResponseModel(BaseModel):
    pass


class GuestTokenResponseModel(BaseModel):
    guest_token: str


class TwitterFlowSubtaskModel(BaseModel):
    subtask_id: str


class TwitterFlowResponseModel(BaseModel):
    flow_token: str
    subtasks: List[TwitterFlowSubtaskModel]
