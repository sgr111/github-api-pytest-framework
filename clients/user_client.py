"""
User API Client — wraps all GitHub /users endpoints.
Follows API Client Class pattern (POM equivalent for REST APIs).
"""

from .base_client import BaseClient
from models import UserModel


class UserClient(BaseClient):

    def get_user(self, username: str):
        """GET /users/{username} — fetch a public user profile"""
        return self.get(f"/users/{username}")

    def get_authenticated_user(self):
        """GET /user — fetch the authenticated user's profile"""
        return self.get("/user")

    def get_user_repos(self, username: str, per_page: int = 10, page: int = 1):
        """GET /users/{username}/repos — list public repos of a user"""
        return self.get(f"/users/{username}/repos", params={
            "per_page": per_page,
            "page": page
        })

    def get_user_followers(self, username: str, per_page: int = 10):
        """GET /users/{username}/followers"""
        return self.get(f"/users/{username}/followers", params={"per_page": per_page})

    def get_user_following(self, username: str, per_page: int = 10):
        """GET /users/{username}/following"""
        return self.get(f"/users/{username}/following", params={"per_page": per_page})

    def get_and_validate_user(self, username: str) -> UserModel:
        """Fetch user and validate schema with Pydantic"""
        response = self.get_user(username)
        self.assert_status(response, 200)
        return UserModel(**response.json())
