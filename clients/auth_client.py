"""
Auth Client — wraps GitHub auth & rate limit endpoints.
"""

from .base_client import BaseClient
from models import RateLimitModel


class AuthClient(BaseClient):

    def get_rate_limit(self):
        """GET /rate_limit — check current API quota"""
        return self.get("/rate_limit")

    def get_authenticated_user(self):
        """GET /user — requires valid token"""
        return self.get("/user")

    def get_and_validate_rate_limit(self) -> RateLimitModel:
        response = self.get_rate_limit()
        self.assert_status(response, 200)
        return RateLimitModel(**response.json())
