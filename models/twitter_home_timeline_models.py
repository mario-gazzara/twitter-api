"""
Twitter Home Timeline Models: most of this models were generated using https://jsontopydantic.com/ and then modified
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TwitterHomeTimelineRequestModel(BaseModel):
    class VariablesModel(BaseModel):
        count: int = 20
        cursor: str | None = None
        includePromotedContent: bool = True
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


class Url(BaseModel):
    url: str
    urlType: str


class Badge(BaseModel):
    url: str


class Label(BaseModel):
    url: Url
    badge: Badge
    description: str
    userLabelType: str
    userLabelDisplayType: str


class AffiliatesHighlightedLabel(BaseModel):
    label: Label


class Url1(BaseModel):
    display_url: str
    expanded_url: str
    url: str
    indices: List[int]


class Description(BaseModel):
    urls: List[Url1]


class Entities(BaseModel):
    description: Description


class Legacy(BaseModel):
    following: bool
    can_dm: bool
    can_media_tag: bool
    created_at: str
    default_profile: bool
    default_profile_image: bool
    description: str
    entities: Entities
    fast_followers_count: int
    favourites_count: int
    followers_count: int
    friends_count: int
    has_custom_timelines: bool
    is_translator: bool
    listed_count: int
    location: str
    media_count: int
    name: str
    normal_followers_count: int
    pinned_tweet_ids_str: List[str]
    possibly_sensitive: bool
    profile_banner_url: str
    profile_image_url_https: str
    profile_interstitial_type: str
    screen_name: str
    statuses_count: int
    translator_type: str
    verified: bool
    want_retweets: bool
    withheld_in_countries: List


class Professional(BaseModel):
    rest_id: str
    professional_type: str
    category: List


class Result1(BaseModel):
    id: str
    rest_id: str
    affiliates_highlighted_label: AffiliatesHighlightedLabel
    has_graduated_access: bool
    is_blue_verified: bool
    profile_image_shape: str
    legacy: Legacy
    professional: Professional
    super_follow_eligible: bool


class UserResults(BaseModel):
    result: Result1


class Core(BaseModel):
    user_results: UserResults


class EditControl(BaseModel):
    edit_tweet_ids: List[str]
    editable_until_msecs: str
    is_edit_eligible: bool
    edits_remaining: str


class Views(BaseModel):
    count: int
    state: str


class Entities1(BaseModel):
    user_mentions: List
    urls: List
    hashtags: List
    symbols: List


class Legacy1(BaseModel):
    bookmark_count: int
    bookmarked: bool
    created_at: str
    conversation_id_str: str
    display_text_range: List[int]
    entities: Entities1
    favorite_count: int
    full_text: str
    is_quote_status: bool
    favorited: bool
    lang: str
    quote_count: int
    reply_count: int
    retweet_count: int
    retweeted: bool
    user_id_str: str
    id_str: str


class Result(BaseModel):
    rest_id: str
    core: Core
    edit_control: EditControl
    is_translatable: bool
    views: Views
    source: str
    legacy: Legacy1


class TweetResults(BaseModel):
    result: Result


class ItemContent(BaseModel):
    itemType: str
    tweet_results: TweetResults
    tweetDisplayType: str


class FeedbackInfo(BaseModel):
    feedbackKeys: List[str]
    feedbackMetadata: str


class TimelinesDetails(BaseModel):
    injectionType: str
    controllerData: str


class Details(BaseModel):
    timelinesDetails: TimelinesDetails


class ClientEventInfo(BaseModel):
    component: str
    element: str
    details: Details


class Content(BaseModel):
    entryType: str
    itemContent: Optional[ItemContent] = None
    feedbackInfo: Optional[FeedbackInfo] = None
    clientEventInfo: Optional[ClientEventInfo] = None
    value: Optional[str] = None
    cursorType: Optional[str] = None


class Entry(BaseModel):
    entryId: str
    sortIndex: str
    content: Content


class Instruction(BaseModel):
    type: str
    entries: List[Entry]


class HomeTimelineUrt(BaseModel):
    instructions: List[Instruction]


class Home(BaseModel):
    home_timeline_urt: HomeTimelineUrt


class Data(BaseModel):
    home: Home


class TwitterHomeTimelineResponseRawModel(BaseModel):
    data: Data


class TwitterHomeTimelineTweetUserModel(BaseModel):
    id: str
    rest_id: str
    full_name: str
    description: str | None
    profile_image_url: str | None
    profile_banner_url: str | None
    verified: bool
    is_blue_verified: bool
    favourites_count: int
    followers_count: int
    friends_count: int


class TwitterHomeTimelineTweetModel(BaseModel):
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
    creator: TwitterHomeTimelineTweetUserModel


class TwitterHomeTimelinePaginationModel(BaseModel):
    previous_cursor: str | None = None
    next_cursor: str | None = None
    total_count: int


class TwitterHomeTimelineResponseModel(BaseModel):
    tweets: List[TwitterHomeTimelineTweetModel]
    pagination: TwitterHomeTimelinePaginationModel
