
# the lines of code below are used to avoid circular imports with type hinting

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.auth.twitter_auth_process import TwitterAuthenticationProcess

# end of the lines of code used to avoid circular imports with type hinting

import abc
import json

from models.twitter_models import TwitterFlowResponseModel


class TwitterAbstractAuthenticationFlow(abc.ABC):
    __flow_token: str | None = None
    __subtask_id: str

    @abc.abstractmethod
    def handle(self, context: TwitterAuthenticationProcess):
        pass

    @property
    def flow_token(self) -> str | None:
        return self.__flow_token

    @flow_token.setter
    def flow_token(self, value: str) -> None:
        self.__flow_token = value

    @property
    def subtask_id(self) -> str:
        return self.__subtask_id

    @subtask_id.setter
    def subtask_id(self, value: str) -> None:
        self.__subtask_id = value


class TwitterInitAuthFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
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

        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            params={'flow_name': 'login'},
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to initialize authentication flow')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)


class LoginJsInstrumentationSubtaskFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginJsInstrumentationSubtask",
                    "js_instrumentation": {
                        "response": json.dumps(
                            {
                                "rf": {
                                    "af07339bbc6d24ced887d705eb0c9fd29b4a7d7ddc21136c9f94d53a4bc774d2": 88,
                                    "a6ce87d6481c6ec4a823548be3343437888441d2a453061c54f8e2eb325856f7": 250,
                                    "a0062ad06384a8afd38a41cd83f31b0dbfdea0eff4b24c69f0dd9095b2fb56d6": 16,
                                    "a929e5913a5715d93491eaffaa139ba4977cbc826a5e2dbcdc81cae0f093db25": 186,
                                },
                                "s": "Q-H-53m1uXImK0F0ogrxRQtCWTH1KIlPbIy0MloowlMa4WNK5ZCcDoXyRs1q_" +
                                "cPbynK73w_wfHG_UVRKKBWRoh6UJtlPS5kMa1p8fEvTYi76hwdzBEzovieR8t86UpeSkSBFYcL8foYKSp6Nop5mQR" +
                                "_QHGyEeleclCPUvzS0HblBJqZZdtUo-6by4BgCyu3eQ4fY5nOF8fXC85mu6k34wo982LMK650NsoPL96DBuloqSZvSHU47" +
                                "wq2uA4xy24UnI2WOc6U9KTvxumtchSYNnXq1HV662B8U2-jWrzvIU4yUHV3JYUO6sbN6j8Ho9JaUNJpJSK7REwqCBQ3yG7iwMAAAAX2Vqcbs",
                            }
                        ),
                        "link": "next_link",
                    },
                }
            ],
        }

        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to execute login js instrumentation subtask')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)


class TwitterEnterUserIdentifierSSOFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterUserIdentifierSSO",
                    "settings_list": {
                        "setting_responses": [
                            {
                                "key": "user_identifier",
                                "response_data": {"text_data": {"result": context.user_id}},
                            }
                        ],
                        "link": "next_link",
                    },
                }
            ],
        }
        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to execute enter user identifier sso subtask')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)


class TwitterEnterAlternateIdentifierFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterAlternateIdentifierSubtask",
                    "enter_text": {"text": context.alternate_id, "link": "next_link"},
                }
            ],
        }

        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to execute enter alternate identifier subtask')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)


class TwitterEnterPasswordFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterPassword",
                    "enter_password": {"password": context.password, "link": "next_link"},
                }
            ],
        }

        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to execute enter password subtask')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)


class TwitterAccountDuplicationCheckFlow(TwitterAbstractAuthenticationFlow):
    def handle(self, context: TwitterAuthenticationProcess):
        payload = {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "AccountDuplicationCheck",
                    "check_logged_in_account": {
                        "link": "AccountDuplicationCheck_false"
                    },
                }
            ],
        }

        response = context.twitter_client.post(
            f'{context.twitter_client.api_base_url}/onboarding/task.json',
            data=payload,
            model_type=TwitterFlowResponseModel
        )

        if not response.is_success or response.data is None:
            raise Exception('Failed to execute enter password subtask')

        data: TwitterFlowResponseModel = response.data

        subtask_id = data.subtasks[0].subtask_id if len(data.subtasks) > 0 else 'None'
        context.set_next_flow(subtask_id, data.flow_token)
