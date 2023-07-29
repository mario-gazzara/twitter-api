import os
import pickle
from datetime import datetime
from http.cookiejar import CookieJar

import requests

from logger import setup_logger

logger = setup_logger(__name__)


class SessionCookiesCacheService:
    __BASE_DIR = '.sessions'

    def __init__(self):
        if not os.path.exists(self.__BASE_DIR):
            os.makedirs(self.__BASE_DIR)

    def save_cookies(self, session: requests.Session, key: str):
        with open(f'{self.__BASE_DIR}/{key}', 'wb') as f:
            pickle.dump(session.cookies, f)

    def load_cookies(self, session: requests.Session, key: str):
        with open(f'{self.__BASE_DIR}/{key}', 'rb') as f:
            session.cookies.update(pickle.load(f))

    def cookies_exists(self, key: str):
        return os.path.exists(f'{self.__BASE_DIR}/{key}')

    def delete_cookies(self, key: str):
        os.remove(f'{self.__BASE_DIR}/{key}')

    def refresh_cookies(self, session: requests.Session, key: str):
        if self.cookies_exists(key):
            self.delete_cookies(key)

        self.save_cookies(session, key)

    def are_cookies_valid(self, key: str):
        try:
            with open(f'{self.__BASE_DIR}/{key}', 'rb') as f:
                cookies: CookieJar = pickle.load(f)
        except (FileNotFoundError, EOFError):
            return False

        for cookie in cookies:
            if cookie.expires and cookie.expires >= datetime.now().timestamp():
                logger.info("Cookie expired")
                return False

        return True
