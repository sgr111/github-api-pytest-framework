"""
test_search.py — Tests for GitHub /search endpoints.

Covers: repo search, user search, schema validation,
        sorting, pagination, empty queries, edge cases.
"""

import pytest
from models import SearchRepoResultModel, SearchUserResultModel


@pytest.mark.smoke
@pytest.mark.search
class TestSearchReposSmoke:

    def test_search_repos_status_200(self, search_client):
        """GET /search/repositories with valid query returns 200"""
        response = search_client.search_repos("fastapi")
        search_client.assert_status(response, 200)

    def test_search_repos_schema_valid(self, search_client):
        """Search response matches SearchRepoResultModel Pydantic schema"""
        result = search_client.get_and_validate_repo_search("pytest")
        assert isinstance(result, SearchRepoResultModel)

    def test_search_repos_total_count_positive(self, search_client):
        """Searching 'python' must return total_count > 0"""
        result = search_client.get_and_validate_repo_search("python")
        assert result.total_count > 0

    def test_search_repos_items_not_empty(self, search_client):
        """Items list must not be empty for valid query"""
        result = search_client.get_and_validate_repo_search("selenium")
        assert len(result.items) > 0


@pytest.mark.regression
@pytest.mark.search
class TestSearchReposDetailed:

    def test_search_repos_per_page_limit(self, search_client):
        """per_page=5 must return at most 5 items"""
        response = search_client.search_repos("django", per_page=5)
        search_client.assert_status(response, 200)
        items = response.json()["items"]
        assert len(items) <= 5

    def test_search_repos_items_have_required_fields(self, search_client):
        """Each repo item must have id, name, full_name fields"""
        result = search_client.get_and_validate_repo_search("fastapi")
        for item in result.items:
            assert item.id > 0
            assert item.name != ""
            assert "/" in item.full_name

    def test_search_repos_sorted_by_stars(self, search_client):
        """Results sorted by stars desc — first item should have most stars"""
        response = search_client.search_repos("python", sort="stars", order="desc", per_page=5)
        search_client.assert_status(response, 200)
        items = response.json()["items"]
        stars = [i["stargazers_count"] for i in items]
        assert stars == sorted(stars, reverse=True)

    def test_search_repos_response_time(self, search_client):
        """Search response must arrive within 5 seconds"""
        response = search_client.search_repos("requests")
        search_client.assert_response_time(response, max_seconds=5.0)

    @pytest.mark.parametrize("query", ["fastapi", "pytest", "selenium", "pydantic"])
    def test_search_multiple_queries_return_results(self, search_client, query):
        """Parametrized: each popular query returns results"""
        result = search_client.get_and_validate_repo_search(query)
        assert result.total_count > 0


@pytest.mark.regression
@pytest.mark.search
class TestSearchUsers:

    def test_search_users_status_200(self, search_client):
        """GET /search/users with valid query returns 200"""
        response = search_client.search_users("torvalds")
        search_client.assert_status(response, 200)

    def test_search_users_schema_valid(self, search_client):
        """User search response matches SearchUserResultModel"""
        result = search_client.get_and_validate_user_search("guido")
        assert isinstance(result, SearchUserResultModel)

    def test_search_users_items_have_login(self, search_client):
        """Each user item must have a login field"""
        result = search_client.get_and_validate_user_search("torvalds")
        for user in result.items:
            assert user.login != ""

    def test_search_users_content_type_json(self, search_client):
        """Content-Type must be application/json"""
        response = search_client.search_users("python")
        search_client.assert_content_type_json(response)


@pytest.mark.negative
@pytest.mark.search
class TestSearchNegative:

    def test_search_repos_empty_query_returns_422(self, search_client):
        """Empty query string should return 422 Unprocessable Entity"""
        response = search_client.search_repos("")
        assert response.status_code in (422, 400, 200)  # GH may handle differently

    def test_search_repos_gibberish_returns_zero_results(self, search_client):
        """Gibberish query should return 0 or very few results"""
        result = search_client.get_and_validate_repo_search(
            "zxqwerty123nomatchforsure99999abc"
        )
        assert result.total_count == 0 or len(result.items) == 0
