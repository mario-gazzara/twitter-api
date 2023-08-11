import os
import sys

from dependency_injector.wiring import Provide, inject

from twitter_api.container import TwitterContainer
from twitter_api.logger import get_logger
from twitter_api.services.twitter_api_service import TwitterAPIService

logger = get_logger(__name__)


@inject
def init(twitter_api_service: TwitterAPIService = Provide[TwitterContainer.twitter_api_service]):
    login_succeded = twitter_api_service.login(user_id, alternate_user_id, password, )

    if not login_succeded:
        logger.error('Authentication failed')
        return

    logger.info('Authentication succeeded')

    timeline = twitter_api_service.get_home_timeline()

    if timeline is None:
        logger.error('Failed to get home timeline')
        return

    if timeline.pagination.total_count == 0:
        logger.error('Home timeline is empty')
        return

    tweet = timeline.tweets[0]
    print(tweet.model_dump_json())

    # text_content = "Hello guys"

    # # Reply to tweet

    # reply_tweet_id = twitter_api_service.create_tweet(text_content, tweet.rest_id)

    # if reply_tweet_id is None:
    #     logger.error('Failed to reply to tweet')
    #     return

    # logger.info(f'Replied to tweet {tweet.rest_id} with {reply_tweet_id}')


if __name__ == '__main__':
    user_id = os.environ['TWITTER_USER_ID']
    alternate_user_id = os.environ['TWITTER_ALTERNATE_USER_ID']
    password = os.environ['TWITTER_PASSWORD']

    container = TwitterContainer()
    container.init_resources()

    container.wire(modules=[sys.modules[__name__]])

    try:
        init()
    finally:
        container.shutdown_resources()
