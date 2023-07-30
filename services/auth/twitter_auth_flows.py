# the lines of code below are used to avoid circular imports with type hinting

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from services.auth.twitter_auth_process import TwitterAuthenticationProcess

# end of the lines of code used to avoid circular imports with type hinting

import abc
import json
from http import HTTPMethod
from typing import Any, Dict

from logger import setup_logger
from models.twitter_models import TwitterFlowResponseModel
from utils import deep_merge

logger = setup_logger(__name__)


class TwitterAbstractAuthenticationFlow(abc.ABC):
    _flow_token: str | None = None
    _subtask_id: str | None = None

    @abc.abstractmethod
    def build_payload(self, context: TwitterAuthenticationProcess) -> Dict[str, Any]:
        pass

    def handle(self, context: TwitterAuthenticationProcess) -> None:
        logger.debug(f'Executing {self.subtask_id or "Init Auth"} subtask')

        payload = self.build_payload(context)

        if self._flow_token is not None and self._subtask_id is not None:
            payload = deep_merge(payload, {
                "flow_token": self._flow_token,
            })

        params = {"flow_name": "login"} if self._flow_token is None else None

        response = context.twitter_client.request(
            HTTPMethod.POST,
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            params=params,
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            logger.error(f'Failed to execute {self.subtask_id} subtask')
            logger.error(f'Response status code: {response.status_code}')

            if response.errors:
                logger.error(f'Response body: {json.dumps([e.model_dump() for e in response.errors], indent=4)}')

            return

        subtask_id = response.data.subtasks[0].subtask_id if len(response.data.subtasks) > 0 else None
        context.set_next_flow(subtask_id, response.data.flow_token)

    @property
    def flow_token(self) -> str | None:
        return self._flow_token

    @flow_token.setter
    def flow_token(self, value: str | None) -> None:
        self._flow_token = value

    @property
    def subtask_id(self) -> str | None:
        return self._subtask_id

    @subtask_id.setter
    def subtask_id(self, value: str | None) -> None:
        self._subtask_id = value


class TwitterInitAuthFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, _: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "input_flow_data": {
                "flow_context": {
                    "debug_overrides": {},
                    "start_location": {"location": "splash_screen"},
                }
            },
            "subtask_versions": {
                "contacts_live_sync_permission_prompt": 0,
                "email_verification": 1,
                "topics_selector": 1,
                "wait_spinner": 1,
                "cta": 4,
            },
        }


class LoginJsInstrumentationSubtaskFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, _: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": self.subtask_id,
                }
            ],
        }


class TwitterEnterUserIdentifierSSOFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": self.subtask_id,
                    "settings_list": {
                        "setting_responses": [
                            {
                                "key": "user_identifier",
                                "response_data": {
                                    "text_data": {
                                        "result": context.user_id
                                    }
                                },
                            }
                        ],
                        "link": "next_link",
                    },
                }
            ],
        }


class TwitterEnterAlternateIdentifierFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": self.subtask_id,
                    "enter_text": {
                        "text": context.alternate_id,
                        "link": "next_link"
                    },
                }
            ],
        }


class TwitterEnterPasswordFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": self.subtask_id,
                    "enter_password": {
                        "password": context.password,
                        "link": "next_link"
                    },
                }
            ],
        }


class TwitterAccountDuplicationCheckFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, _: TwitterAuthenticationProcess) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": self.subtask_id,
                    "check_logged_in_account": {
                        "link": "AccountDuplicationCheck_false"
                    },
                }
            ],
        }
