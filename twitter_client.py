import random
import time
from typing import Any, Callable, Dict, Generic, Type, TypeVar

import requests
from pydantic import BaseModel, FieldValidationInfo, field_validator

from logger import setup_logger
from models.twitter_models import GuestTokenResponseModel

logger = setup_logger(__name__)


class TwitterClientOptions(BaseModel):
    MIN_WAIT_TIME: int = 1
    MAX_WAIT_TIME: int = 20
    DEFAULT_MIN_WAIT_TIME: int = 2
    DEFAULT_MAX_WAIT_TIME: int = 5

    proxies: Dict[str, str] | None = None
    min_wait_time: int = DEFAULT_MIN_WAIT_TIME
    max_wait_time: int = DEFAULT_MAX_WAIT_TIME

    @field_validator('min_wait_time', 'max_wait_time')
    @classmethod
    def validate_wait_times(cls, v: int, info: FieldValidationInfo) -> int:
        if v <= cls.MIN_WAIT_TIME or v >= cls.MAX_WAIT_TIME:
            raise ValueError(f"{info.field_name} must be greater than {cls.MIN_WAIT_TIME} and lower than {cls.MAX_WAIT_TIME}")

        return v

    @field_validator('min_wait_time', 'max_wait_time')
    @classmethod
    def validate_min_max_times(cls, v: int, info: FieldValidationInfo) -> int:
        if 'max_wait_time' in info.data and v >= info.data['max_wait_time']:
            raise ValueError("min_wait_time must be less than max_wait_time")

        return v


T = TypeVar("T", bound=BaseModel)


class TwitterAPIResponse(BaseModel, Generic[T]):
    is_success: bool
    status_code: int
    data: T | None = None
    cookies: Dict[str, str]


class TwitterClient:
    DEFAULT_LANG: str = "en"

    __session: requests.Session
    __options: TwitterClientOptions | None = None

    def __init__(self, options: TwitterClientOptions | None = None) -> None:
        self.__options = options
        self.__hydratate_session()

    def __enter__(self) -> "TwitterClient":
        self.__session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__session.close()

    def delayed_request(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore
        def wrapper(self: "TwitterClient", *args, **kwargs):
            wait_time = random.uniform(
                self.options.min_wait_time if self.options else TwitterClientOptions.DEFAULT_MIN_WAIT_TIME,
                self.options.max_wait_time if self.options else TwitterClientOptions.DEFAULT_MAX_WAIT_TIME)

            time.sleep(wait_time)
            return func(*args, **kwargs)

        return wrapper

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
    def headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'Content-Type': 'application/json',
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": self.lang,
        }

    @property
    def api_base_url(self) -> str:
        return "https://api.twitter.com/1.1"

    @property
    def base_url(self) -> str:
        return "https://twitter.com"

    @property
    def lang(self) -> str:
        return self.DEFAULT_LANG

    def get(self, url: str, params: Dict[str, Any] = {}, model_type: Type[T] | None = None) -> TwitterAPIResponse:
        response = self.__session.get(url, headers=self.headers, params=params, proxies=self.options.proxies if self.options else None)

        response.raise_for_status()  # Check for any HTTP errors in the response

        model_response = model_type and self.__deserialize_response_to_model(response, model_type)

        return TwitterAPIResponse(
            is_success=response.ok,
            status_code=response.status_code,
            data=model_response,
            cookies=response.cookies.get_dict()
        )

    def post(self, url: str, params: Dict[str, Any] = {}, data: Dict[str, Any] = {}, model_type: Type[T] | None = None) -> TwitterAPIResponse:
        response = self.__session.post(url, headers=self.headers, params=params, json=data, proxies=self.options.proxies if self.options else None)

        response.raise_for_status()  # Check for any HTTP errors in the response

        model_response = model_type and self.__deserialize_response_to_model(response, model_type)

        return TwitterAPIResponse(
            is_success=response.ok,
            status_code=response.status_code,
            data=model_response,
            cookies=response.cookies.get_dict()
        )

    def __hydratate_session(self) -> None:
        """
        Hydratate the session with base cookies and headers, guest token and csrf token
        """
        response = self.get(self.base_url)

        if not response.is_success:
            raise Exception("Failed to hydratate session")

        response = self.post(f"{self.api_base_url}/guest/activate.json", model_type=GuestTokenResponseModel)
        data: GuestTokenResponseModel | None = response.data

        if not response.is_success or data is None:
            raise Exception("Failed to get guest token")

        self.headers.update({
            'x-guest-token': data.guest_token,
            'x-csrf-token': response.cookies.get("ct0"),
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        })

    def __deserialize_response_to_model(self, response: requests.Response, model_type: Type[T]) -> T | None:
        """
        Deserialize a requests.Response object to a Pydantic model.

        Args:
            response (requests.Response): The response object from the API.
            model_type (Type[T]): The Pydantic model type.

        Returns:
            T | None: An instance of the Pydantic model if deserialization succeeds, otherwise None.
        """
        try:
            json_data = response.json()
            return model_type.model_validate(json_data)
        except (requests.exceptions.HTTPError, ValueError, TypeError, KeyError) as e:
            logger.error("Error occurred during deserialization: %s", e)
            return None
