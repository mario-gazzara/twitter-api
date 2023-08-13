from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, computed_field


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
    favourites_count: int | None = 0
    followers_count: int | None = 0
    friends_count: int | None = 0
    name: str
    screen_name: str
    profile_banner_url: str | None = None
    profile_image_url_https: str | None
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
    count: int | None = 0


class TweetLegacy(BaseModel):
    bookmark_count: int | None = 0
    bookmarked: bool
    created_at: str
    favorite_count: int | None = 0
    full_text: str
    favorited: bool
    lang: str
    quote_count: int | None = 0
    reply_count: int | None = 0
    retweet_count: int | None = 0
    retweeted_status_result: Dict[str, Any] | None = None
    retweeted: bool
    id_str: str


class TweetResult(BaseModel):
    rest_id: str | None = None
    core: Core | None = None
    views: Views | None = None
    legacy: TweetLegacy | None = None


class TweetResults(BaseModel):
    result: TweetResult | None = None


class CreateTweet(BaseModel):
    tweet_results: TweetResults | None = None


class Data(BaseModel):
    create_tweet: CreateTweet | None = None


class TwitterTweetResponseModel(BaseModel):
    data: Data


class TwitterUserModel(BaseModel):
    id: str
    rest_id: str
    full_name: str
    username: str
    description: str | None
    profile_image_url: str | None
    profile_banner_url: str | None = None
    verified: bool
    is_blue_verified: bool
    favourites_count: int | None
    followers_count: int | None
    friends_count: int | None


class TwitterTweetModel(BaseModel):
    id: str
    rest_id: str
    is_retweet: bool
    view_count: int | None
    bookmark_count: int | None
    favorite_count: int | None
    quote_count: int | None
    reply_count: int | None
    retweet_count: int | None
    favorited: bool
    bookmarked: bool
    retweeted: bool
    content: str
    lang: str
    created_at: datetime
    author: TwitterUserModel

    @computed_field
    @property
    def uri(self) -> str:
        return f"https://twitter.com/{self.author.username}/status/{self.rest_id}"
