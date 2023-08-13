# the lines of code below are used to avoid circular imports caused by type hinting

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from twitter_api.services.modules.auth.twitter_auth_context import TwitterAuthenticationContext

# end of the lines of code used to avoid circular imports with type hinting

import abc
import json
from http import HTTPMethod
from typing import Any, Dict

from twitter_api.logger import get_logger
from twitter_api.models.twitter_models import TwitterFlowResponseModel
from twitter_api.utils import deep_merge

logger = get_logger(__name__)


class TwitterAbstractAuthenticationFlow(abc.ABC):
    @abc.abstractmethod
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        pass

    def handle(self, context: TwitterAuthenticationContext) -> Tuple[str | None, str | None]:
        logger.debug(f'Executing {context.subtask_id or "Init Auth"} subtask')

        payload = self.build_payload(context)

        if context.flow_token is not None and context.subtask_id is not None:
            payload = deep_merge(payload, {
                "flow_token": context.flow_token,
            })

        params = {"flow_name": "login"} if context.flow_token is None else None

        response = context.twitter_client.request(
            HTTPMethod.POST,
            f'{context.twitter_client.api_base_url_v_1_1}/onboarding/task.json',
            params=params,
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            logger.error(f'Failed to execute {context.subtask_id} subtask')
            logger.error(f'Response status code: {response.status_code}')

            if response.errors:
                logger.error(f'Response body: {json.dumps([e.model_dump() for e in response.errors], indent=4)}')

            return None, None

        subtask_id = response.data.subtasks[0].subtask_id if len(response.data.subtasks) > 0 else None

        return response.data.flow_token, subtask_id


class TwitterInitAuthFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, _: TwitterAuthenticationContext) -> Dict[str, Any]:
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
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": context.subtask_id,
                }
            ],
        }


class TwitterEnterUserIdentifierSSOFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": context.subtask_id,
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
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": context.subtask_id,
                    "enter_text": {
                        "text": context.alternate_id,
                        "link": "next_link"
                    },
                }
            ],
        }


class TwitterEnterPasswordFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": context.subtask_id,
                    "enter_password": {
                        "password": context.password,
                        "link": "next_link"
                    },
                }
            ],
        }


class TwitterAccountDuplicationCheckFlow(TwitterAbstractAuthenticationFlow):
    def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
        return {
            "subtask_inputs": [
                {
                    "subtask_id": context.subtask_id,
                    "check_logged_in_account": {
                        "link": "AccountDuplicationCheck_false"
                    },
                }
            ],
        }


# class TwitterLoginACIDFlow(TwitterAbstractAuthenticationFlow):
#     def build_payload(self, context: TwitterAuthenticationContext) -> Dict[str, Any]:
#         return {
#             "subtask_inputs": [
#                 {
#                     "subtask_id": context.subtask_id,
#                     "enter_text": {
#                         "text": context.acid,
#                         "link": "next_link"
#                     }
#                 }
#             ]
#         }
