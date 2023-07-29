from services.auth.session.cookies_cache_service_interface import CookiesCacheServiceInterface
from services.auth.session.local_cookies_cache_service import LocalCookiesCacheService
from services.auth.twitter_auth_process import TwitterAuthenticationProcess, TwitterAuthFlows
from twitter_client import TwitterClient


class TwitterAPIService:
    __twitter_client: TwitterClient
    __cookies_cache_service: CookiesCacheServiceInterface

    # use local cookies cache service by default
    def __init__(self, twitter_client: TwitterClient, cookies_cache_service: CookiesCacheServiceInterface = LocalCookiesCacheService()):
        self.__twitter_client = twitter_client
        self.__cookies_cache_service = cookies_cache_service

    def authenticate(self, user_id: str, alternate_id: str, password: str, persist_session: bool = True) -> None:
        if persist_session:
            if (self.__cookies_cache_service.cookies_exists(user_id) and
                    self.__cookies_cache_service.are_cookies_valid(user_id)):
                self.__cookies_cache_service.load_cookies(self.__twitter_client.session, user_id)

        context = TwitterAuthenticationProcess(self.__twitter_client, user_id, alternate_id, password)

        # it raises an exception if the authentication process fails
        while context.flow != TwitterAuthFlows.SUCCESS_EXIT:
            context.handle()

        if persist_session:
            self.__cookies_cache_service.save_cookies(self.__twitter_client.session, user_id)
