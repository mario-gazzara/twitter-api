
from typing import List
import requests


class CookiesCacheServiceInterface:
    """
    This interface is used to define the methods that a cookies cache service must implement.
    In this way, be using dependency injection, we can easily change the cookies cache service implementation
    and store the cookies in a database, in a remote server, etc.
    """

    def save_cookies(self, session: requests.Session, key: str) -> None:
        raise NotImplementedError

    def load_cookies(self, session: requests.Session, key: str) -> None:
        raise NotImplementedError

    def cookies_exists(self, key: str) -> bool:
        raise NotImplementedError

    def delete_cookies(self, key: str) -> None:
        raise NotImplementedError

    def refresh_cookies(self, session: requests.Session, key: str):
        raise NotImplementedError

    def are_cookies_valid(self, key: str, cookies_to_check: List[str] | None = None) -> bool:
        raise NotImplementedError
