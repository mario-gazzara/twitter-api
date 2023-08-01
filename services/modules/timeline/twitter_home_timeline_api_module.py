
from datetime import datetime
from http import HTTPMethod
from typing import Generator, List, Literal

from logger import get_logger
from models.twitter_home_timeline_models import TwitterHomeTimelinePaginationModel
from models.twitter_home_timeline_models import \
    TwitterHomeTimelineRequestModel as TwtHomeTimelineReqModel
from models.twitter_home_timeline_models import (
    TwitterHomeTimelineResponseModel, TwitterHomeTimelineResponseRawModel,
    TwitterTweetModel
)
from models.twitter_tweets_models import TwitterUserModel
from twitter_client import TwitterClient

SortType = Literal['ASC', 'DESC']

logger = get_logger(__name__)


class TwitterHomeTimelineAPIModule:
    __twitter_client: TwitterClient

    def __init__(self, twitter_client: TwitterClient):
        self.__twitter_client = twitter_client

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
            legacy = result.legacy

            if legacy is None:
                continue

            user = item_content.tweet_results.result.core.user_results.result

            tweets.append(TwitterTweetModel(
                id=legacy.id_str,
                rest_id=result.rest_id,
                view_count=result.views.count,
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
                    description=user.legacy.description,
                    profile_image_url=user.legacy.profile_image_url_https,
                    profile_banner_url=user.legacy.profile_banner_url,
                    verified=user.legacy.verified,
                    is_blue_verified=user.is_blue_verified,
                    favourites_count=user.legacy.favourites_count,
                    followers_count=user.legacy.followers_count,
                    friends_count=user.legacy.friends_count,
                )
            ))

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
