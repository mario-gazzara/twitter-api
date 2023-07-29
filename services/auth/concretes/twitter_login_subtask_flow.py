
import json

from models.twitter_models import TwitterFlowResponseModel
from services.auth.abstracts.twitter_abstract_flow import AbstractFlow, TwitterAuthContext
from services.auth.twitter_flows import TwitterAuthFlows


class TwitterLoginJsInstrumentationSubtaskFlow(AbstractFlow):
    def handle(self, context: TwitterAuthContext) -> str:
        if context.subtask_id == TwitterAuthFlows.LOGIN_JS_INSTRUMENTATION_SUBTASK.value:
            payload = {
                "flow_token": context.flow_token,
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

            return context.subtask_id
        else:
            return super().handle(context)
