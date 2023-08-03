from datetime import datetime
from http import HTTPMethod

from twitter_api.logger import get_logger
from twitter_api.models.twitter_tweets_models import (
    Reply, TweetResult, TwitterCreateTweetRequestModel, TwitterTweetModel,
    TwitterTweetResponseModel, TwitterUserModel, Variables
)
from twitter_api.twitter_client import TwitterClient

logger = get_logger(__name__)


class TwitterTweetsAPIModule:
    __twitter_client: TwitterClient

    def __init__(self, twitter_client: TwitterClient) -> None:
        self.__twitter_client = twitter_client

    def create_tweet(self, content: str, in_reply_to_tweet_id: str | None = None) -> str | None:
        """
        Create a tweet, optionally in reply to a tweet by providing the tweet rest id
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

    def build_tweet_response(self, tweet_result: TweetResult) -> TwitterTweetModel | None:
        legacy = tweet_result.legacy

        if legacy is None:
            return None

        core = tweet_result.core

        if core is None:
            return None

        user = core.user_results.result

        views = tweet_result.views

        if views is None:
            return None

        if tweet_result.rest_id is None:
            return None

        return TwitterTweetModel(
            id=legacy.id_str,
            rest_id=tweet_result.rest_id,
            view_count=views.count,
            bookmark_count=legacy.bookmark_count,
            favorite_count=legacy.favorite_count,
            quote_count=legacy.quote_count,
            reply_count=legacy.reply_count,
            retweet_count=legacy.retweet_count,
            favorited=legacy.favorited,
            bookmarked=legacy.bookmarked,
            retweeted=legacy.retweeted,
            content=legacy.full_text,
            lang=legacy.lang,
            created_at=datetime.strptime(legacy.created_at, "%a %b %d %H:%M:%S %z %Y"),
            author=TwitterUserModel(
                id=user.id,
                rest_id=user.rest_id,
                full_name=user.legacy.name,
                username=user.legacy.screen_name,
                description=user.legacy.description,
                profile_image_url=user.legacy.profile_image_url_https,
                profile_banner_url=user.legacy.profile_banner_url,
                verified=user.legacy.verified,
                is_blue_verified=user.is_blue_verified,
                favourites_count=user.legacy.favourites_count,
                followers_count=user.legacy.followers_count,
                friends_count=user.legacy.friends_count,
            )
        )

    def get_tweet_details(self, tweet_id: str):
        raise NotImplementedError()
