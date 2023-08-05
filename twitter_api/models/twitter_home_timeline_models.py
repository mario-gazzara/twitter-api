"""
Twitter Home Timeline Models: most of this models were generated using https://jsontopydantic.com/ and then modified
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from twitter_api.models.twitter_tweets_models import TweetResult, TwitterTweetModel


class TwitterHomeTimelineRequestModel(BaseModel):
    class VariablesModel(BaseModel):
        count: int = 20
        cursor: str | None = None
        includePromotedContent: bool = False  # exclude promoted tweets
        latestControlAvailable: bool = True
        requestContext: str = "launch"
        withCommunity: bool = True
        seenTweetIds: List[str] = []

    class FeaturesModel(BaseModel):
        rweb_lists_timeline_redesign_enabled: bool = True
        responsive_web_graphql_exclude_directive_enabled: bool = True
        verified_phone_label_enabled: bool = False
        creator_subscriptions_tweet_preview_api_enabled: bool = True
        responsive_web_graphql_timeline_navigation_enabled: bool = True
        responsive_web_graphql_skip_user_profile_image_extensions_enabled: bool = False
        tweetypie_unmention_optimization_enabled: bool = True
        responsive_web_edit_tweet_api_enabled: bool = True
        graphql_is_translatable_rweb_tweet_is_translatable_enabled: bool = True
        view_counts_everywhere_api_enabled: bool = True
        longform_notetweets_consumption_enabled: bool = True
        responsive_web_twitter_article_tweet_consumption_enabled: bool = False
        tweet_awards_web_tipping_enabled: bool = False
        freedom_of_speech_not_reach_fetch_enabled: bool = True
        standardized_nudges_misinfo: bool = True
        tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled: bool = True
        longform_notetweets_rich_text_read_enabled: bool = True
        longform_notetweets_inline_media_enabled: bool = True
        responsive_web_media_download_video_enabled: bool = False
        responsive_web_enhance_cards_enabled: bool = False

    class FieldTogglesModel(BaseModel):
        withAuxiliaryUserLabels: bool = False
        withArticleRichContentState: bool = False

    variables: VariablesModel = VariablesModel()
    features: FeaturesModel = FeaturesModel()
    fieldToggles: FieldTogglesModel = FieldTogglesModel()
    queryId: str


class TweetResults(BaseModel):
    result: TweetResult


class ItemContent(BaseModel):
    tweet_results: TweetResults


class Content(BaseModel):
    itemContent: Optional[ItemContent] = None
    value: Optional[str] = None


class Entry(BaseModel):
    entryId: str
    sortIndex: str
    content: Content


class Instruction(BaseModel):
    entries: List[Entry]


class HomeTimelineUrt(BaseModel):
    instructions: List[Instruction]


class Home(BaseModel):
    home_timeline_urt: HomeTimelineUrt


class Data(BaseModel):
    home: Home


class TwitterHomeTimelineResponseRawModel(BaseModel):
    data: Data


class TwitterHomeTimelinePaginationModel(BaseModel):
    previous_cursor: str | None = None
    next_cursor: str | None = None
    total_count: int


class TwitterHomeTimelineResponseModel(BaseModel):
    tweets: List[TwitterTweetModel]
    pagination: TwitterHomeTimelinePaginationModel
