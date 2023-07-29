from __future__ import annotations

from abc import ABC, abstractmethod

from services.auth.twitter_flows import TwitterAuthFlows
from twitter_client import TwitterClient


class TwitterAuthContext:
    twitter_client: TwitterClient
    user_id: str
    alternate_id: str
    password: str
    subtask_id: str
    flow_token: str | None = None

    def __init__(self, twitter_client: TwitterClient, user_id: str, alternate_id: str, password: str, subtask_id: str):
        self.twitter_client = twitter_client
        self.user_id = user_id
        self.alternate_id = alternate_id
        self.password = password
        self.subtask_id = subtask_id

    def set_next_flow(self, subtask_id: str, token: str):
        self.subtask_id = subtask_id
        self.flow_token = token


class Flow(ABC):
    @abstractmethod
    def set_next(self, flow: Flow) -> Flow:
        pass

    @abstractmethod
    def handle(self, context: TwitterAuthContext) -> str:
        pass


class AbstractFlow(Flow):
    _next_flow: Flow | None = None

    def set_next(self, flow: Flow) -> Flow:
        self._next_flow = flow

        return flow

    @abstractmethod
    def handle(self, context: TwitterAuthContext) -> str:
        if self._next_flow:
            return self._next_flow.handle(context)

        return TwitterAuthFlows.FAILURE_EXIT.value
