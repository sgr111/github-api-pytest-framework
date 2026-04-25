"""
Search API Client — wraps GitHub /search endpoints.
"""

from .base_client import BaseClient
from models import SearchRepoResultModel, SearchUserResultModel


class SearchClient(BaseClient):

    def search_repos(self, query: str, sort: str = "stars", order: str = "desc", per_page: int = 10):
        """GET /search/repositories"""
        return self.get("/search/repositories", params={
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        })

    def search_users(self, query: str, per_page: int = 10):
        """GET /search/users"""
        return self.get("/search/users", params={
            "q": query,
            "per_page": per_page
        })

    def search_code(self, query: str, per_page: int = 10):
        """GET /search/code"""
        return self.get("/search/code", params={
            "q": query,
            "per_page": per_page
        })

    def get_and_validate_repo_search(self, query: str) -> SearchRepoResultModel:
        response = self.search_repos(query)
        self.assert_status(response, 200)
        return SearchRepoResultModel(**response.json())

    def get_and_validate_user_search(self, query: str) -> SearchUserResultModel:
        response = self.search_users(query)
        self.assert_status(response, 200)
        return SearchUserResultModel(**response.json())
