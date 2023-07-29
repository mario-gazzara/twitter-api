from models.twitter_models import TwitterFlowResponseModel
from services.auth.abstracts.twitter_abstract_flow import AbstractFlow, TwitterAuthContext
from services.auth.twitter_flows import TwitterAuthFlows


class TwitterInitAuthFlow(AbstractFlow):
    def handle(self, context: TwitterAuthContext) -> str:
        if context.subtask_id == TwitterAuthFlows.INIT_AUTH.value:
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

            return context.subtask_id
        else:
            return super().handle(context)
