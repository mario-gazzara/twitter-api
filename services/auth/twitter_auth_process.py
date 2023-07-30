
import enum
from typing import Dict

from logger import setup_logger
from services.auth.twitter_auth_flows import (
    LoginJsInstrumentationSubtaskFlow, TwitterAbstractAuthenticationFlow,
    TwitterAccountDuplicationCheckFlow, TwitterEnterAlternateIdentifierFlow,
    TwitterEnterPasswordFlow, TwitterEnterUserIdentifierSSOFlow, TwitterInitAuthFlow
)
from twitter_client import TwitterClient

logger = setup_logger(__name__)


class TwitterAuthFlows(str, enum.Enum):
    LOGIN_JS_INSTRUMENTATION_SUBTASK = 'LoginJsInstrumentationSubtask'
    LOGIN_ENTER_USER_IDENTIFIER_SSO = 'LoginEnterUserIdentifierSSO'
    LOGIN_ENTER_ALTERNATE_IDENTIFIER = 'LoginEnterAlternateIdentifierSubtask'
    LOGIN_ENTER_PASSWORD = 'LoginEnterPassword'
    ACCOUNT_DUPLICATION_CHECK = 'AccountDuplicationCheck'
    LOGIN_SUCCESS_SUBTASK = 'LoginSuccessSubtask',
    LOGIN_FAILURE_SUBTASK = 'LoginFailureSubtask'


TwitterAurhFlowsToStatesMap: Dict[str, TwitterAbstractAuthenticationFlow] = {
    TwitterAuthFlows.LOGIN_JS_INSTRUMENTATION_SUBTASK.value: LoginJsInstrumentationSubtaskFlow(),
    TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO.value: TwitterEnterUserIdentifierSSOFlow(),
    TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO.value: TwitterEnterUserIdentifierSSOFlow(),
    TwitterAuthFlows.LOGIN_ENTER_ALTERNATE_IDENTIFIER.value: TwitterEnterAlternateIdentifierFlow(),
    TwitterAuthFlows.LOGIN_ENTER_PASSWORD.value: TwitterEnterPasswordFlow(),
    TwitterAuthFlows.ACCOUNT_DUPLICATION_CHECK.value: TwitterAccountDuplicationCheckFlow()
}


class TwitterAuthenticationProcess:
    twitter_client: TwitterClient
    user_id: str
    alternate_id: str
    password: str
    is_authenticated: bool = False
    is_error: bool = False

    __flow: TwitterAbstractAuthenticationFlow

    def __init__(self, twitter_client: TwitterClient, user_id: str, alternate_id: str, password: str):
        self.__flow = TwitterInitAuthFlow()
        self.twitter_client = twitter_client
        self.user_id = user_id
        self.alternate_id = alternate_id
        self.password = password

    def handle(self):
        self.__flow.handle(self)

    def set_next_flow(self, subtask_id: str | None, token: str | None):
        if subtask_id == TwitterAuthFlows.LOGIN_SUCCESS_SUBTASK.value:
            self.is_authenticated = True
            logger.info('Successfully authenticated')
            return

        if subtask_id == TwitterAuthFlows.LOGIN_FAILURE_SUBTASK.value:
            self.is_error = True
            logger.info('Authentication failed')
            return

        next_flow = TwitterAurhFlowsToStatesMap.get(subtask_id) if subtask_id is not None else None

        if next_flow is None:
            raise Exception(f'Flow not handled: {subtask_id}')

        self.__flow = next_flow
        self.__flow.flow_token = token
        self.__flow.subtask_id = subtask_id
