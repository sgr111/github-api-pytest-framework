"""
Base API Client — wraps requests.Session with auth headers,
base URL, and shared response helpers.

This is the "POM equivalent" for API testing:
instead of Page Objects, we have API Client Classes.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()


class BaseClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.session = requests.Session()
        token = os.getenv("GITHUB_TOKEN")
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def get(self, endpoint: str, params: dict = None) -> requests.Response:
        url = f"{self.BASE_URL}{endpoint}"
        return self.session.get(url, params=params)

    def post(self, endpoint: str, json: dict = None) -> requests.Response:
        url = f"{self.BASE_URL}{endpoint}"
        return self.session.post(url, json=json)

    def patch(self, endpoint: str, json: dict = None) -> requests.Response:
        url = f"{self.BASE_URL}{endpoint}"
        return self.session.patch(url, json=json)

    def delete(self, endpoint: str) -> requests.Response:
        url = f"{self.BASE_URL}{endpoint}"
        return self.session.delete(url)

    def assert_status(self, response: requests.Response, expected: int):
        assert response.status_code == expected, (
            f"Expected {expected}, got {response.status_code}. "
            f"Body: {response.text[:300]}"
        )

    def assert_response_time(self, response: requests.Response, max_seconds: float = 3.0):
        elapsed = response.elapsed.total_seconds()
        assert elapsed < max_seconds, (
            f"Response too slow: {elapsed:.2f}s (max {max_seconds}s)"
        )

    def assert_content_type_json(self, response: requests.Response):
        ct = response.headers.get("Content-Type", "")
        assert "application/json" in ct, f"Unexpected Content-Type: {ct}"
