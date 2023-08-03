import json
import os
from typing import List

import requests

from twitter_api.logger import get_logger
from twitter_api.services.modules.auth.session.cookies_cache_service_interface import (
    CookiesCacheServiceInterface
)

logger = get_logger(__name__)


class LocalCookiesCacheService(CookiesCacheServiceInterface):
    __base_dir = '.sessions'
    __file_format = '.json'

    def __init__(self, base_dir: str | None = None):
        # use the default base dir if no base dir is provided
        if base_dir:
            self.__base_dir = base_dir

        if not os.path.exists(self.__base_dir):
            os.makedirs(self.__base_dir)

    def build_path(self, key: str) -> str:
        return f'{self.__base_dir}/{key}{self.__file_format}'

    def save_cookies(self, session: requests.Session, key: str) -> None:
        cookies = []

        for cookie in session.cookies:
            cookies.append({
                'version': cookie.version,
                'name': cookie.name,
                'value': cookie.value,
                'port': cookie.port,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expires': cookie.expires,
                'discard': cookie.discard,
                'comment': cookie.comment,
                'comment_url': cookie.comment_url,
                'rfc2109': cookie.rfc2109,
            })

        with open(self.build_path(key), 'w') as f:
            json.dump(cookies, f)

    def load_cookies(self, session: requests.Session, key: str) -> None:
        raise NotImplementedError()

    def are_cookies_valid(self, key: str, cookies_to_check: List[str] | None = None) -> bool:
        raise NotImplementedError

    def refresh_cookies(self, session: requests.Session, key: str):
        raise NotImplementedError

    def cookies_exists(self, key: str) -> bool:
        raise NotImplementedError

    def delete_cookies(self, key: str) -> None:
        raise NotImplementedError
