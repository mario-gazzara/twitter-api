from dependency_injector import containers, providers

from services.modules.auth.session.local_cookies_cache_service import LocalCookiesCacheService
from services.modules.auth.twitter_auth_api_module import TwitterAuthAPIModule
from services.modules.timeline.twitter_home_timeline_api_module import TwitterHomeTimelineAPIModule
from services.modules.tweets.twitter_tweets_api_module import TwitterTweetsAPIModule
from services.twitter_api_service import TwitterAPIService
from twitter_client import TwitterClient, TwitterClientOptions


def init_twitter_client(min_wait_time: int, max_wait_time: int):
    with TwitterClient(
        TwitterClientOptions(
            min_wait_time=min_wait_time,
            max_wait_time=max_wait_time,
        )
    ) as twitter_client:
        yield twitter_client


class TwitterContainer(containers.DeclarativeContainer):
    twitter_client = providers.Resource(init_twitter_client, min_wait_time=1, max_wait_time=2)

    cookie_cache_service = providers.Singleton(LocalCookiesCacheService)

    twitter_auth_api_module = providers.Singleton(
        TwitterAuthAPIModule,
        twitter_client=twitter_client,
        cookies_cache_service=cookie_cache_service
    )

    twitter_tweets_api_module = providers.Singleton(
        TwitterTweetsAPIModule,
        twitter_client=twitter_client
    )

    twitter_home_timeline_api_module = providers.Singleton(
        TwitterHomeTimelineAPIModule,
        twitter_client=twitter_client,
        twitter_tweets_api_module=twitter_tweets_api_module
    )

    twitter_api_service = providers.Singleton(
        TwitterAPIService,
        twitter_auth_api_module=twitter_auth_api_module,
        twitter_tweets_api_module=twitter_tweets_api_module,
        twitter_home_timeline_api_module=twitter_home_timeline_api_module
    )
