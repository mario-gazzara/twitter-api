
import enum
from typing import Dict, Tuple

from twitter_api.logger import get_logger
from twitter_api.services.modules.auth.twitter_auth_flows import (
    LoginJsInstrumentationSubtaskFlow, TwitterAbstractAuthenticationFlow,
    TwitterAccountDuplicationCheckFlow, TwitterEnterAlternateIdentifierFlow,
    TwitterEnterPasswordFlow, TwitterEnterUserIdentifierSSOFlow, TwitterInitAuthFlow
)
from twitter_api.twitter_client import TwitterClient

logger = get_logger(__name__)


class TwitterAuthFlows(str, enum.Enum):
    LOGIN_JS_INSTRUMENTATION_SUBTASK = 'LoginJsInstrumentationSubtask'
    LOGIN_ENTER_USER_IDENTIFIER_SSO = 'LoginEnterUserIdentifierSSO'
    LOGIN_ENTER_ALTERNATE_IDENTIFIER = 'LoginEnterAlternateIdentifierSubtask'
    LOGIN_ENTER_PASSWORD = 'LoginEnterPassword'
    ACCOUNT_DUPLICATION_CHECK = 'AccountDuplicationCheck'
    LOGIN_SUCCESS_SUBTASK = 'LoginSuccessSubtask',
    LOGIN_FAILURE_SUBTASK = 'LoginFailureSubtask'


TW_AUTH_FLOWS_TO_STATES: Dict[str, TwitterAbstractAuthenticationFlow] = {
    TwitterAuthFlows.LOGIN_JS_INSTRUMENTATION_SUBTASK.value: LoginJsInstrumentationSubtaskFlow(),
    TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO.value: TwitterEnterUserIdentifierSSOFlow(),
    TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO.value: TwitterEnterUserIdentifierSSOFlow(),
    TwitterAuthFlows.LOGIN_ENTER_ALTERNATE_IDENTIFIER.value: TwitterEnterAlternateIdentifierFlow(),
    TwitterAuthFlows.LOGIN_ENTER_PASSWORD.value: TwitterEnterPasswordFlow(),
    TwitterAuthFlows.ACCOUNT_DUPLICATION_CHECK.value: TwitterAccountDuplicationCheckFlow()
}


class TwitterAuthenticationContext:
    twitter_client: TwitterClient
    user_id: str
    alternate_id: str
    password: str
    flow_token: str | None = None
    subtask_id: str | None = None

    __flow: TwitterAbstractAuthenticationFlow

    def __init__(self, twitter_client: TwitterClient, user_id: str, alternate_id: str, password: str):
        self.__flow = TwitterInitAuthFlow()
        self.twitter_client = twitter_client
        self.user_id = user_id
        self.alternate_id = alternate_id
        self.password = password

    def handle(self) -> Tuple[str | None, str | None]:
        return self.__flow.handle(self)

    def set_flow(self, flow: TwitterAbstractAuthenticationFlow) -> None:
        self.__flow = flow
