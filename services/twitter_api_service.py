from logger import setup_logger
from services.auth.abstracts.twitter_abstract_flow import TwitterAuthContext
from services.auth.concretes.twitter_account_dup_check_flow import (
    TwitterAccountDuplicationCheckFlow
)
from services.auth.concretes.twitter_enter_alternate_id_flow import (
    TwitterEnterAlternateIdentifierFlow
)
from services.auth.concretes.twitter_enter_password_flow import TwitterEnterPasswordFlow
from services.auth.concretes.twitter_enter_user_id_sso_flow import TwitterEnterUserIdentifierSSOFlow
from services.auth.concretes.twitter_init_auth_flow import TwitterInitAuthFlow
from services.auth.concretes.twitter_login_subtask_flow import (
    TwitterLoginJsInstrumentationSubtaskFlow
)
from services.auth.twitter_flows import TwitterAuthFlows
from services.cookies_cache_service import SessionCookiesCacheService
from twitter_client import TwitterClient

logger = setup_logger(__name__)

TWITTER_AUTH_FLOWS_ORDER = [
    TwitterAuthFlows.INIT_AUTH,
    TwitterAuthFlows.LOGIN_JS_INSTRUMENTATION_SUBTASK,
    TwitterAuthFlows.LOGIN_ENTER_USER_IDENTIFIER_SSO,
    TwitterAuthFlows.LOGIN_ENTER_ALTERNATE_IDENTIFIER,
    TwitterAuthFlows.LOGIN_ENTER_PASSWORD,
    TwitterAuthFlows.ACCOUNT_DUPLICATION_CHECK
]


class TwitterAPIService:
    __twitter_client: TwitterClient
    __cookies_cache_service: SessionCookiesCacheService

    def __init__(self, twitter_client: TwitterClient, cookies_cache_service: SessionCookiesCacheService):
        self.__twitter_client = twitter_client
        self.__cookies_cache_service = cookies_cache_service

    def authenticate(self, user_id: str, alternate_id: str, password: str) -> None:
        if (self.__cookies_cache_service.cookies_exists(user_id) and
                self.__cookies_cache_service.are_cookies_valid(user_id)):
            self.__cookies_cache_service.load_cookies(self.__twitter_client.session, user_id)
            return

        auth_flow = TwitterInitAuthFlow()  # Init auth flow is the first flow in the chain

        (auth_flow
            .set_next(TwitterLoginJsInstrumentationSubtaskFlow())  # This is the second flow in the chain (I don't know exactly why it is needed)
            .set_next(TwitterEnterUserIdentifierSSOFlow())  # Enter user email/phone number
            .set_next(TwitterEnterAlternateIdentifierFlow())  # Enter username
            .set_next(TwitterEnterPasswordFlow())  # Enter password
            .set_next(TwitterAccountDuplicationCheckFlow()))  # Check if account is duplicated

        for flow in TWITTER_AUTH_FLOWS_ORDER:
            subtask_id = auth_flow.handle(TwitterAuthContext(
                self.__twitter_client,
                user_id,
                alternate_id,
                password,
                flow.value
            ))

            if subtask_id == TwitterAuthFlows.SUCCESS_EXIT.value:
                logger.info('Successfully authenticated')
                break

            if subtask_id == TwitterAuthFlows.FAILURE_EXIT.value:
                logger.info('Failed to authenticate')
                break
