
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
    SUCCESS_EXIT = 'SuccessExit'


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

    __flow: TwitterAbstractAuthenticationFlow

    def __init__(self, twitter_client: TwitterClient, user_id: str, alternate_id: str, password: str):
        self.__flow = TwitterInitAuthFlow()
        self.twitter_client = twitter_client
        self.user_id = user_id
        self.alternate_id = alternate_id
        self.password = password

    def handle(self):
        self.__flow.handle(self)

    @property
    def flow(self) -> TwitterAbstractAuthenticationFlow:
        return self.__flow

    def set_next_flow(self, subtask_id: str, token: str):
        if subtask_id == TwitterAuthFlows.SUCCESS_EXIT.value:
            logger.info('Successfully authenticated')
            return

        next_flow = TwitterAurhFlowsToStatesMap.get(subtask_id)

        if next_flow is None:
            raise Exception(f'Flow not handled: {subtask_id}')

        self.__flow = next_flow
        self.__flow.flow_token = token
        self.__flow.subtask_id = subtask_id
