
from http import HTTPMethod
from typing import Generator, List, Literal

from twitter_api.logger import get_logger
from twitter_api.models.twitter_home_timeline_models import TwitterHomeTimelinePaginationModel
from twitter_api.models.twitter_home_timeline_models import \
    TwitterHomeTimelineRequestModel as TwtHomeTimelineReqModel
from twitter_api.models.twitter_home_timeline_models import (
    TwitterHomeTimelineResponseModel, TwitterHomeTimelineResponseRawModel, TwitterTweetModel
)
from twitter_api.services.modules.tweets.twitter_tweets_api_module import TwitterTweetsAPIModule
from twitter_api.twitter_client import TwitterClient

SortType = Literal['ASC', 'DESC']

logger = get_logger(__name__)


class TwitterHomeTimelineAPIModule:
    __twitter_client: TwitterClient
    __twitter_tweets_api_module: TwitterTweetsAPIModule

    def __init__(self, twitter_client: TwitterClient, twitter_tweets_api_module: TwitterTweetsAPIModule):
        self.__twitter_client = twitter_client
        self.__twitter_tweets_api_module = twitter_tweets_api_module

    def get_home_timeline_tweets_stream(
            self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> Generator[TwitterTweetModel, None, None]:
        """
        Get a stream of home timeline tweets pages, sorted by created_at, default is from newest to oldest.
        Please note that you need to be authenticated to use this method.
        """

        while True:
            response = self.get_home_timeline(count, cursor, sort)

            if response is None:
                return None

            cursor = response.pagination.next_cursor

            for tweet in response.tweets:
                yield tweet

            if cursor is None:
                break

    def get_home_timeline_stream(
            self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> Generator[TwitterHomeTimelineResponseModel, None, None]:
        """
        Get a stream of home timeline tweets sorted by created_at, default is from newest to oldest.
        Please note that you need to be authenticated to use this method.
        """
        while True:
            timeline = self.get_home_timeline(count, cursor, sort)

            if timeline is None:
                return None

            cursor = timeline.pagination.next_cursor

            yield timeline

            if cursor is None:
                break

    def get_home_timeline(self, count: int = 20, cursor: str | None = None, sort: SortType = 'DESC') -> TwitterHomeTimelineResponseModel | None:
        """
        Get home timeline tweets sorted by created_at, default is from newest to oldest.
        Please note that you need to be authenticated to use this method.
        """
        query_id = 'W4Tpu1uueTGK53paUgxF0Q'
        endpoint = f'{self.__twitter_client.gql_url}/{query_id}/HomeTimeline'
        payload = TwtHomeTimelineReqModel(
            queryId=query_id,
            variables=TwtHomeTimelineReqModel.VariablesModel(
                count=count,
                cursor=cursor)).model_dump()

        response = self.__twitter_client.request(
            HTTPMethod.POST,
            endpoint,
            data=payload,
            model_type=TwitterHomeTimelineResponseRawModel
        )

        if not response.is_success or response.data is None:
            logger.error('Failed to get home timeline')
            logger.error(f'Response status code: {response.status_code}')

            if response.errors:
                logger.error(f'Response body: {response.errors}')

            return None

        pretty_response = self.__prepare_home_timeline_response(response.data)

        pretty_response.tweets.sort(key=lambda tweet: tweet.created_at, reverse=sort == 'DESC')

        return pretty_response

    def __prepare_home_timeline_response(self, raw_response: TwitterHomeTimelineResponseRawModel) -> TwitterHomeTimelineResponseModel:
        """
        Prepare home timeline response to be more readable.
        """
        empty_response = TwitterHomeTimelineResponseModel(
            tweets=[],
            pagination=TwitterHomeTimelinePaginationModel(
                next_cursor=None,
                previous_cursor=None,
                total_count=0
            )
        )

        instructions = raw_response.data.home.home_timeline_urt.instructions

        if len(instructions) == 0:
            return empty_response

        entries = instructions[0].entries

        if len(entries) == 0:
            return empty_response

        tweets: List[TwitterTweetModel] = []
        tweet_entries_raw = [entry for entry in entries if entry.entryId.startswith('tweet')]

        for tweet_entry_raw in tweet_entries_raw:
            item_content = tweet_entry_raw.content.itemContent

            if item_content is None:
                continue

            result = item_content.tweet_results.result

            tweet = self.__twitter_tweets_api_module.build_tweet_response(result)

            # exclude retweets
            if tweet is None or 'RT @' in tweet.content:
                continue

            tweets.append(tweet)

        cursor_entries = [entry for entry in entries if entry.entryId.startswith('cursor')]

        top_cursor = next((entry.content.value for entry in cursor_entries if entry.entryId.startswith('cursor-top')), None)
        bottom_cursor = next((entry.content.value for entry in cursor_entries if entry.entryId.startswith('cursor-bottom')), None)
        total_count = len(tweets)

        return TwitterHomeTimelineResponseModel(
            tweets=tweets,
            pagination=TwitterHomeTimelinePaginationModel(
                previous_cursor=top_cursor,
                next_cursor=bottom_cursor,
                total_count=total_count
            )
        )
