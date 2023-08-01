import random
import time
from http import HTTPMethod
from typing import Any, Dict, Generic, List, Type, TypeVar

import requests
from pydantic import BaseModel, FieldValidationInfo, field_validator

from logger import get_logger
from models.twitter_models import EmptyResponseModel, GuestTokenResponseModel

logger = get_logger(__name__)


MIN_WAIT_TIME: int = 1
MAX_WAIT_TIME: int = 5


class TwitterClientOptions(BaseModel):
    proxies: Dict[str, str] | None = None
    min_wait_time: int = MIN_WAIT_TIME
    max_wait_time: int = MAX_WAIT_TIME

    @field_validator('min_wait_time', 'max_wait_time')
    @classmethod
    def validate_wait_times(cls, v: int, info: FieldValidationInfo) -> int:
        if v < 1 or v > 20:
            raise ValueError(f"{info.field_name} must be greater than 1 and lower than 20 seconds")

        return v

    @field_validator('min_wait_time', 'max_wait_time')
    @classmethod
    def validate_min_max_times(cls, v: int, info: FieldValidationInfo) -> int:
        if 'max_wait_time' in info.data and v >= info.data['max_wait_time']:
            raise ValueError("min_wait_time must be less than max_wait_time")

        return v


T = TypeVar("T", bound=BaseModel)


class TwitterAPIErrorResponse(BaseModel):
    code: int
    message: str


class TwitterAPIResponse(BaseModel, Generic[T]):
    is_success: bool
    status_code: int
    data: T | None = None
    errors: List[TwitterAPIErrorResponse] | None = None


class TwitterClient:
    # This bearer token is used to authenticate requests to the Twitter API and seems to be always the same,
    # I don't know if it's a good idea to hardcode it but it's the only way I found to make requests to the API
    __DEFAULT_BEARER_TOKEN: str = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    __DEFAULT_LANG: str = "en"

    __session: requests.Session
    __options: TwitterClientOptions | None = None
    __headers: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Content-Type': 'application/json',
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": __DEFAULT_LANG,
    }

    def __init__(self, options: TwitterClientOptions | None = None) -> None:
        self.__options = options

    def __enter__(self) -> "TwitterClient":
        self.__session = requests.Session()
        self.__get_guest_token()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__session.close()

    @property
    def session(self) -> requests.Session:
        return self.__session

    @property
    def options(self) -> TwitterClientOptions | None:
        return self.__options

    @options.setter
    def options(self, options: TwitterClientOptions) -> None:
        self.__options = options

    @property
    def headers(self) -> Dict[str, Any]:
        self.__headers.update({'x-csrf-token': self.__session.cookies.get('ct0') or ''})
        return self.__headers

    @headers.setter
    def headers(self, headers: Dict[str, Any]) -> None:
        self.__headers = headers

    @property
    def api_base_url_v_1_1(self) -> str:
        return "https://api.twitter.com/1.1"

    @property
    def base_url(self) -> str:
        return "https://twitter.com"

    @property
    def gql_url(self) -> str:
        return "https://twitter.com/i/api/graphql"

    def request(
            self,
            method: HTTPMethod,
            url: str,
            model_type: Type[T],
            headers: Dict[str, Any] | None = None,
            params: Dict[str, Any] | None = None,
            data: Dict[str, Any] | None = None) -> 'TwitterAPIResponse[T]':
        headers = headers or self.headers

        wait_time = random.randint(
            self.__options.min_wait_time if self.__options else MIN_WAIT_TIME,
            self.__options.max_wait_time if self.__options else MAX_WAIT_TIME)

        time.sleep(wait_time)

        response = self.__session.request(
            method.value.lower(),
            url,
            headers=headers,
            params=params,
            json=data,
            proxies=self.__options.proxies if self.__options else None)

        if 400 <= response.status_code and response.status_code < 500:
            logger.warning(f"Request failed with status code {response.status_code} and body {response.text}")

            try:
                errors_json = response.json()
                errors = [TwitterAPIErrorResponse(**error) for error in errors_json['errors'] if 'errors' in errors_json]

            except ValueError:
                errors = None

            return TwitterAPIResponse[T](
                is_success=False,
                status_code=response.status_code,
                errors=errors
            )

        response.raise_for_status()

        model_response = self.__deserialize_response_to_model(response, model_type)

        return TwitterAPIResponse[T](
            is_success=response.ok,
            status_code=response.status_code,
            data=model_response
        )

    def __get_guest_token(self) -> None:
        self.__headers.update({'Authorization': f'Bearer {self.__DEFAULT_BEARER_TOKEN}'})
        guest_response = self.request(HTTPMethod.POST, f"{self.api_base_url_v_1_1}/guest/activate.json", model_type=GuestTokenResponseModel)

        if not guest_response.is_success or guest_response.data is None or guest_response.data.guest_token is None:
            raise Exception("Failed to hydratate session: missing guest token")

        self.headers.update({'x-guest-token': guest_response.data.guest_token})

    def __deserialize_response_to_model(self, response: requests.Response, model_type: Type[T]) -> T:
        if model_type is EmptyResponseModel:
            return model_type()

        try:
            json_data = response.json()
            return model_type.model_validate(json_data)
        except (requests.exceptions.HTTPError, ValueError, TypeError, KeyError) as e:
            logger.error("Error occurred during deserialization: %s", e)
            raise e
