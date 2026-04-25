"""
test_auth.py — Tests for GitHub auth & rate limit endpoints.

Covers: valid token auth, rate limit schema, quota checks,
        invalid token handling, unauthenticated access.
"""

import pytest
import requests as req
from models import RateLimitModel


@pytest.mark.smoke
@pytest.mark.ratelimit
class TestAuthSmoke:

    def test_get_rate_limit_status_200(self, auth_client):
        """GET /rate_limit returns 200 with valid token"""
        response = auth_client.get_rate_limit()
        auth_client.assert_status(response, 200)

    def test_get_rate_limit_schema_valid(self, auth_client):
        """Rate limit response matches RateLimitModel Pydantic schema"""
        result = auth_client.get_and_validate_rate_limit()
        assert isinstance(result, RateLimitModel)

    def test_get_authenticated_user_status_200(self, auth_client):
        """GET /user returns 200 with valid token"""
        response = auth_client.get_authenticated_user()
        auth_client.assert_status(response, 200)

    def test_get_authenticated_user_has_login(self, auth_client):
        """Authenticated user response must have login field"""
        response = auth_client.get_authenticated_user()
        body = response.json()
        assert "login" in body
        assert body["login"] != ""


@pytest.mark.regression
@pytest.mark.ratelimit
class TestRateLimitDetailed:

    def test_rate_limit_has_core_resource(self, auth_client):
        """Rate limit response must include 'core' in resources"""
        result = auth_client.get_and_validate_rate_limit()
        assert "core" in result.resources

    def test_rate_limit_has_search_resource(self, auth_client):
        """Rate limit response must include 'search' in resources"""
        result = auth_client.get_and_validate_rate_limit()
        assert "search" in result.resources

    def test_rate_limit_remaining_non_negative(self, auth_client):
        """Remaining requests must be >= 0"""
        result = auth_client.get_and_validate_rate_limit()
        assert result.rate.remaining >= 0

    def test_rate_limit_limit_is_positive(self, auth_client):
        """Total rate limit must be a positive integer"""
        result = auth_client.get_and_validate_rate_limit()
        assert result.rate.limit > 0

    def test_rate_limit_authenticated_higher_than_5000(self, auth_client):
        """Authenticated users get at least 5000 requests/hour"""
        result = auth_client.get_and_validate_rate_limit()
        assert result.rate.limit >= 5000

    def test_rate_limit_response_time(self, auth_client):
        """Rate limit endpoint must respond within 3 seconds"""
        response = auth_client.get_rate_limit()
        auth_client.assert_response_time(response, 3.0)

    def test_rate_limit_reset_is_unix_timestamp(self, auth_client):
        """reset field must be a large unix timestamp (after year 2020)"""
        result = auth_client.get_and_validate_rate_limit()
        assert result.rate.reset > 1_577_836_800  # Jan 1, 2020 in unix time


@pytest.mark.negative
@pytest.mark.ratelimit
class TestAuthNegative:

    def test_invalid_token_returns_401(self):
        """Invalid Bearer token must return 401 Unauthorized"""
        response = req.get(
            "https://api.github.com/user",
            headers={
                "Authorization": "Bearer this_is_a_completely_invalid_token_xyz",
                "Accept": "application/vnd.github+json",
            }
        )
        assert response.status_code == 401

    def test_invalid_token_error_message(self):
        """401 response must contain a meaningful error message"""
        response = req.get(
            "https://api.github.com/user",
            headers={
                "Authorization": "Bearer invalid_token_test_abc123",
                "Accept": "application/vnd.github+json",
            }
        )
        body = response.json()
        assert "message" in body

    def test_no_token_public_endpoint_still_works(self):
        """Public endpoints work without auth (but with lower rate limit)"""
        response = req.get(
            "https://api.github.com/users/torvalds",
            headers={"Accept": "application/vnd.github+json"}
        )
        assert response.status_code == 200
