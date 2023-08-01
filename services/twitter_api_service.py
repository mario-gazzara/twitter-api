

from functools import wraps
from typing import Generator

from logger import get_logger
from models.twitter_home_timeline_models import (
    TwitterHomeTimelineResponseModel, TwitterHomeTimelineTweetModel
)
from services.modules.auth.twitter_auth_api_module import TwitterAuthAPIModule
from services.modules.timeline.twitter_home_timeline_api_module import (
    SortType, TwitterHomeTimelineAPIModule
)

logger = get_logger(__name__)


def authenticated(func):
    @wraps(func)
    def wrapper(self: 'TwitterAPIService', *args, **kwargs):
        if self.is_authenticated:
            return func(self, *args, **kwargs)
        else:
            raise ValueError("Not authenticated. Please log in before using this method.")

    return wrapper


class TwitterAPIService:
    __twitter_auth_api_module: TwitterAuthAPIModule
    __twitter_home_timeline_api_module: TwitterHomeTimelineAPIModule

    def __init__(
            self,
            twitter_auth_api_module: TwitterAuthAPIModule,
            twitter_home_timeline_api_module: TwitterHomeTimelineAPIModule):
        self.__twitter_home_timeline_api_module = twitter_home_timeline_api_module
        self.__twitter_auth_api_module = twitter_auth_api_module

    @property
    def is_authenticated(self) -> bool:
        return self.__twitter_auth_api_module.is_authenticated

    def login(self, user_id: str, alternate_id: str, password: str, persist_session: bool = True) -> bool:
        return self.__twitter_auth_api_module.login(user_id, alternate_id, password, persist_session)

    @authenticated
    def get_home_timeline_tweets_stream(
            self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> Generator[TwitterHomeTimelineTweetModel, None, None]:
        return self.__twitter_home_timeline_api_module.get_home_timeline_tweets_stream(count, cursor, sort)

    @authenticated
    def get_home_timeline_stream(
            self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> Generator[TwitterHomeTimelineResponseModel, None, None]:
        return self.__twitter_home_timeline_api_module.get_home_timeline_stream(count, cursor, sort)

    @authenticated
    def get_home_timeline(self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> TwitterHomeTimelineResponseModel | None:
        return self.__twitter_home_timeline_api_module.get_home_timeline(count, cursor, sort)
