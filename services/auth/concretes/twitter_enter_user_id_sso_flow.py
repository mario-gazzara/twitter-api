from models.twitter_models import TwitterFlowResponseModel
from services.auth.abstracts.twitter_abstract_flow import AbstractFlow, TwitterAuthContext
from services.auth.twitter_flows import TwitterAuthFlows


class TwitterEnterUserIdentifierSSOFlow(AbstractFlow):
    def handle(self, context: TwitterAuthContext) -> str:
        if context.subtask_id == TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO.value:
            payload = {
                "flow_token": context.flow_token,
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

            return context.subtask_id
        else:
            return super().handle(context)
