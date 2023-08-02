from logger import get_logger
from services.modules.auth.session.cookies_cache_service_interface import (
    CookiesCacheServiceInterface
)
from services.modules.auth.session.local_cookies_cache_service import LocalCookiesCacheService
from services.modules.auth.twitter_auth_context import (
    TW_AUTH_FLOWS_TO_STATES, TwitterAuthenticationContext, TwitterAuthFlows
)
from twitter_client import TwitterClient

logger = get_logger(__name__)


class TwitterAuthAPIModule:
    __twitter_client: TwitterClient
    __cookies_cache_service: CookiesCacheServiceInterface
    __is_authenticated: bool = False

    def __init__(
            self,
            twitter_client: TwitterClient,
            cookies_cache_service: CookiesCacheServiceInterface = LocalCookiesCacheService()):
        self.__twitter_client = twitter_client
        self.__cookies_cache_service = cookies_cache_service

    @property
    def is_authenticated(self) -> bool:
        return self.__is_authenticated

    def login(self, user_id: str, alternate_id: str, password: str, persist_session: bool = True) -> bool:
        """
        Login to twitter account, persist session by default using cookies cache service with local strategy
        """
        if (
            persist_session and
            self.__cookies_cache_service.cookies_exists(user_id) and
            self.__cookies_cache_service.are_cookies_valid(user_id, cookies_to_check=[
                'auth_token', 'ct0', 'guest_id', 'kdt', 'twid'
            ])
        ):
            self.__cookies_cache_service.load_cookies(self.__twitter_client.session, user_id)

            logger.info('Loading cookies from cache...')

            self.__is_authenticated = True
            return self.__is_authenticated

        auth_context = TwitterAuthenticationContext(self.__twitter_client, user_id, alternate_id, password)

        while True:
            flow_token, subtask_id = auth_context.handle()

            if subtask_id == TwitterAuthFlows.LOGIN_SUCCESS_SUBTASK.value:
                logger.info('Successfully authenticated')

                if persist_session:
                    self.__cookies_cache_service.save_cookies(self.__twitter_client.session, user_id)

                self.__is_authenticated = True
                return self.__is_authenticated

            if subtask_id == TwitterAuthFlows.LOGIN_FAILURE_SUBTASK.value:
                logger.info('Authentication failed')

                return False

            elif subtask_id is None:
                logger.warning('Next flow is not defined')
                return False

            next_flow = TW_AUTH_FLOWS_TO_STATES.get(subtask_id) if subtask_id is not None else None

            if next_flow is None:
                logger.warning(f'Flow not handled: {subtask_id}')
                return False

            auth_context.flow_token = flow_token
            auth_context.subtask_id = subtask_id

            auth_context.set_flow(next_flow)
