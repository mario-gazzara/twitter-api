import os
import pickle
from datetime import datetime
from http.cookiejar import CookieJar

import requests

from logger import setup_logger
from services.auth.session.cookies_cache_service_interface import CookiesCacheServiceInterface

logger = setup_logger(__name__)


class LocalCookiesCacheService(CookiesCacheServiceInterface):
    __base_dir = '.sessions'

    def __init__(self, base_dir: str | None = None):
        if base_dir:
            self.__base_dir = base_dir

        if not os.path.exists(self.__base_dir):
            os.makedirs(self.__base_dir)

    def save_cookies(self, session: requests.Session, key: str) -> None:
        with open(f'{self.__base_dir}/{key}', 'wb') as f:
            pickle.dump(session.cookies, f)

    def load_cookies(self, session: requests.Session, key: str) -> None:
        with open(f'{self.__base_dir}/{key}', 'rb') as f:
            session.cookies.update(pickle.load(f))

    def cookies_exists(self, key: str) -> bool:
        return os.path.exists(f'{self.__base_dir}/{key}')

    def delete_cookies(self, key: str) -> None:
        os.remove(f'{self.__base_dir}/{key}')

    def refresh_cookies(self, session: requests.Session, key: str):
        if self.cookies_exists(key):
            self.delete_cookies(key)

        self.save_cookies(session, key)

    def are_cookies_valid(self, key: str) -> bool:
        try:
            with open(f'{self.__base_dir}/{key}', 'rb') as f:
                cookies: CookieJar = pickle.load(f)
        except (FileNotFoundError, EOFError):
            return False

        for cookie in cookies:
            if cookie.expires and cookie.expires >= datetime.now().timestamp():
                logger.info("Cookie expired")
                return False

        return True
