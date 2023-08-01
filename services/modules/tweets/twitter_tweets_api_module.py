from http import HTTPMethod

from logger import get_logger
from models.twitter_tweets_models import (
    Reply, TwitterCreateTweetRequestModel, TwitterTweetResponseModel, Variables
)
from twitter_client import TwitterClient

logger = get_logger(__name__)


class TwitterTweetsAPIModule:
    __twitter_client: TwitterClient

    def __init__(self, twitter_client: TwitterClient) -> None:
        self.__twitter_client = twitter_client

    def create_tweet(self, content: str, in_reply_to_tweet_id: str | None = None) -> str | None:
        """
        Create a tweet, optionally in reply to a tweet by providing the tweet id
        Returns the tweet id of the created tweet
        """
        query_id = 'SoVnbfCycZ7fERGCwpZkYA'
        endpoint = f'{self.__twitter_client.gql_url}/{query_id}/CreateTweet'

        reply: Reply | None = None

        if in_reply_to_tweet_id is not None:
            reply = Reply(in_reply_to_tweet_id=in_reply_to_tweet_id)

        payload = TwitterCreateTweetRequestModel(
            variables=Variables(
                tweet_text=content,
                reply=reply
            ),
            queryId=query_id
        ).model_dump(exclude_none=True)

        response = self.__twitter_client.request(
            HTTPMethod.POST,
            endpoint,
            data=payload,
            model_type=TwitterTweetResponseModel
        )

        if not response.is_success or response.data is None:
            logger.error('Failed to create tweet')

            logger.error(f'Response status code: {response.status_code}')

            if response.errors:
                logger.error(f'Response body: {response.errors}')

            return None

        return response.data.data.create_tweet.tweet_results.result.rest_id
