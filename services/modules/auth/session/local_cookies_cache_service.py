import os
import pickle
from datetime import datetime
from http.cookiejar import CookieJar

import requests

from logger import get_logger
from services.modules.auth.session.cookies_cache_service_interface import (
    CookiesCacheServiceInterface
)

logger = get_logger(__name__)


class LocalCookiesCacheService(CookiesCacheServiceInterface):
    __base_dir = '.sessions'
    __file_format = '.pkr'

    def __init__(self, base_dir: str | None = None):
        # use the default base dir if no base dir is provided
        if base_dir:
            self.__base_dir = base_dir

        if not os.path.exists(self.__base_dir):
            os.makedirs(self.__base_dir)

    def build_path(self, key: str) -> str:
        return f'{self.__base_dir}/{key}{self.__file_format}'

    def save_cookies(self, session: requests.Session, key: str) -> None:
        with open(self.build_path(key), 'wb') as f:
            pickle.dump(session.cookies, f)

    def load_cookies(self, session: requests.Session, key: str) -> None:
        with open(self.build_path(key), 'rb') as f:
            session.cookies.update(pickle.load(f))

    def cookies_exists(self, key: str) -> bool:
        return os.path.exists(self.build_path(key))

    def delete_cookies(self, key: str) -> None:
        os.remove(self.build_path(key))

    def refresh_cookies(self, session: requests.Session, key: str):
        if self.cookies_exists(key):
            self.delete_cookies(key)

        self.save_cookies(session, key)

    def are_cookies_valid(self, key: str) -> bool:
        try:
            with open(self.build_path(key), 'rb') as f:
                cookies: CookieJar = pickle.load(f)
        except (FileNotFoundError, EOFError):
            return False

        for cookie in cookies:
            if cookie.expires and cookie.expires <= datetime.utcnow().timestamp():
                logger.info("Cookie expired")
                return False

        return True
