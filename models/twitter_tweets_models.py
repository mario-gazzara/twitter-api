from datetime import datetime
from typing import List

from pydantic import BaseModel


class MediaEntity(BaseModel):
    media_entities: List[str] = []
    possibly_sensitive: bool = False


class Reply(BaseModel):
    in_reply_to_tweet_id: str
    exclude_reply_user_ids: List[str] = []


class Variables(BaseModel):
    tweet_text: str
    reply: Reply | None = None
    dark_request: bool = False
    media: MediaEntity = MediaEntity()
    semantic_annotation_ids: List[str] = []


class Features(BaseModel):
    tweetypie_unmention_optimization_enabled: bool = True
    responsive_web_edit_tweet_api_enabled: bool = True
    graphql_is_translatable_rweb_tweet_is_translatable_enabled: bool = True
    view_counts_everywhere_api_enabled: bool = True
    longform_notetweets_consumption_enabled: bool = True
    responsive_web_twitter_article_tweet_consumption_enabled: bool = False
    tweet_awards_web_tipping_enabled: bool = False
    longform_notetweets_rich_text_read_enabled: bool = True
    longform_notetweets_inline_media_enabled: bool = True
    responsive_web_graphql_exclude_directive_enabled: bool = True
    verified_phone_label_enabled: bool = False
    freedom_of_speech_not_reach_fetch_enabled: bool = True
    standardized_nudges_misinfo: bool = True
    tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled: bool = True
    responsive_web_media_download_video_enabled: bool = False
    responsive_web_graphql_skip_user_profile_image_extensions_enabled: bool = False
    responsive_web_graphql_timeline_navigation_enabled: bool = True
    responsive_web_enhance_cards_enabled: bool = False


class FieldToggles(BaseModel):
    withArticleRichContentState: bool = False
    withAuxiliaryUserLabels: bool = False


class TwitterCreateTweetRequestModel(BaseModel):
    variables: Variables
    features: Features = Features()
    fieldToggles: FieldToggles = FieldToggles()
    queryId: str


class UserLegacy(BaseModel):
    description: str
    favourites_count: int = 0
    followers_count: int = 0
    friends_count: int = 0
    name: str
    profile_banner_url: str | None = None
    profile_image_url_https: str
    verified: bool


class UserResult(BaseModel):
    id: str
    rest_id: str
    is_blue_verified: bool
    legacy: UserLegacy


class UserResults(BaseModel):
    result: UserResult


class Core(BaseModel):
    user_results: UserResults


class Views(BaseModel):
    count: int = 0


class TweetEntities(BaseModel):
    user_mentions: List
    urls: List
    hashtags: List
    symbols: List


class TweetLegacy(BaseModel):
    bookmark_count: int = 0
    bookmarked: bool
    created_at: str
    entities: TweetEntities
    favorite_count: int = 0
    full_text: str
    favorited: bool
    lang: str
    quote_count: int = 0
    reply_count: int = 0
    retweet_count: int = 0
    retweeted: bool
    id_str: str


class TweetResult(BaseModel):
    rest_id: str
    core: Core
    views: Views
    source: str
    legacy: TweetLegacy | None = None


class TweetResults(BaseModel):
    result: TweetResult


class CreateTweet(BaseModel):
    tweet_results: TweetResults


class Data(BaseModel):
    create_tweet: CreateTweet


class TwitterTweetResponseModel(BaseModel):
    data: Data


class TwitterUserModel(BaseModel):
    id: str
    rest_id: str
    full_name: str
    description: str | None
    profile_image_url: str | None
    profile_banner_url: str | None = None
    verified: bool
    is_blue_verified: bool
    favourites_count: int
    followers_count: int
    friends_count: int


class TwitterTweetModel(BaseModel):
    id: str
    rest_id: str
    view_count: int
    bookmark_count: int
    favorite_count: int
    quote_count: int
    reply_count: int
    retweet_count: int
    favorited: bool
    bookmarked: bool
    retweeted: bool
    content: str
    lang: str
    created_at: datetime
    author: TwitterUserModel
