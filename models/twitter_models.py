from typing import List

from pydantic import BaseModel


class EmptyResponseModel(BaseModel):
    pass


class GuestTokenResponseModel(BaseModel):
    guest_token: str


class TwitterFlowResponseModel(BaseModel):
    class TwitterFlowSubtaskModel(BaseModel):
        subtask_id: str

    flow_token: str
    subtasks: List[TwitterFlowSubtaskModel]
