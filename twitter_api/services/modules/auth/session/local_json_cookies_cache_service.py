import json
import os
from datetime import datetime
from http.cookiejar import CookieJar
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
            cookie_dict = {
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
            }

            cookies.append(cookie_dict)

        with open(self.build_path(key), 'w') as f:
            json.dump(cookies, f)

    def load_cookies(self, session: requests.Session, key: str) -> None:
        with open(self.build_path(key), 'rb') as f:
            for cookie in json.load(f):
                session.cookies.set_cookie(
                    requests.cookies.create_cookie(**cookie)  # type: ignore
                )

    def are_cookies_valid(self, key: str, cookies_to_check: List[str] | None = None) -> bool:
        try:
            cookies = CookieJar()
            with open(self.build_path(key), 'rb') as f:
                for cookie in json.load(f):
                    cookies.set_cookie(requests.cookies.create_cookie(**cookie))  # type: ignore

            for cookie in cookies:
                if cookies_to_check and cookie.name not in cookies_to_check:
                    continue

                if cookie.expires and cookie.expires <= datetime.utcnow().timestamp():
                    logger.warning("Cookie expired")
                    return False

            return True
        except (FileNotFoundError, EOFError):
            return False

    def refresh_cookies(self, session: requests.Session, key: str):
        if self.cookies_exists(key):
            self.delete_cookies(key)

        self.save_cookies(session, key)

    def cookies_exists(self, key: str) -> bool:
        return os.path.exists(self.build_path(key))

    def delete_cookies(self, key: str) -> None:
        os.remove(self.build_path(key))
