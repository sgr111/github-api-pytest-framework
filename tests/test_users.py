"""
test_users.py — Tests for GitHub /users endpoints.

Covers: positive, negative, schema validation, response time,
        pagination, auth, and edge cases.
"""

import pytest
from models import UserModel


@pytest.mark.smoke
@pytest.mark.users
class TestUserPositive:

    def test_get_known_user_status_200(self, user_client, known_user):
        """GET /users/{username} returns 200 for a valid user"""
        response = user_client.get_user(known_user)
        user_client.assert_status(response, 200)

    def test_get_known_user_schema_valid(self, validated_user):
        """Response matches UserModel Pydantic schema"""
        assert isinstance(validated_user, UserModel)

    def test_get_known_user_login_matches(self, validated_user, known_user):
        """login field in response matches requested username"""
        assert validated_user.login == known_user

    def test_get_known_user_has_positive_repos(self, validated_user):
        """Known user should have at least 1 public repo"""
        assert validated_user.public_repos >= 1

    def test_get_known_user_content_type_json(self, user_client, known_user):
        """Content-Type header must be application/json"""
        response = user_client.get_user(known_user)
        user_client.assert_content_type_json(response)

    def test_get_known_user_response_time(self, user_client, known_user):
        """Response must arrive within 3 seconds"""
        response = user_client.get_user(known_user)
        user_client.assert_response_time(response, max_seconds=3.0)

    def test_get_known_user_id_is_integer(self, validated_user):
        """User id field must be a positive integer"""
        assert isinstance(validated_user.id, int)
        assert validated_user.id > 0

    def test_get_known_user_avatar_url_present(self, validated_user):
        """avatar_url must be a non-empty string"""
        assert validated_user.avatar_url.startswith("https://")

    def test_get_known_user_type_is_user(self, validated_user):
        """type field must be 'User' for individual accounts"""
        assert validated_user.type == "User"


@pytest.mark.regression
@pytest.mark.users
class TestUserRepos:

    def test_get_user_repos_status_200(self, user_client, known_user):
        """GET /users/{username}/repos returns 200"""
        response = user_client.get_user_repos(known_user)
        user_client.assert_status(response, 200)

    def test_get_user_repos_returns_list(self, user_client, known_user):
        """Response body must be a JSON array"""
        response = user_client.get_user_repos(known_user)
        assert isinstance(response.json(), list)

    def test_get_user_repos_pagination(self, user_client, known_user):
        """per_page=5 must return at most 5 repos"""
        response = user_client.get_user_repos(known_user, per_page=5)
        user_client.assert_status(response, 200)
        assert len(response.json()) <= 5

    def test_get_user_repos_each_has_name(self, user_client, known_user):
        """Every repo in the list must have a 'name' field"""
        response = user_client.get_user_repos(known_user, per_page=10)
        repos = response.json()
        assert all("name" in repo for repo in repos)

    def test_get_user_followers_status_200(self, user_client, known_user):
        """GET /users/{username}/followers returns 200"""
        response = user_client.get_user_followers(known_user)
        user_client.assert_status(response, 200)


@pytest.mark.negative
@pytest.mark.users
class TestUserNegative:

    def test_get_nonexistent_user_returns_404(self, user_client):
        """GET /users/{invalid} must return 404"""
        response = user_client.get_user("this-user-definitely-does-not-exist-xyz123abc")
        user_client.assert_status(response, 404)

    def test_get_nonexistent_user_error_message(self, user_client):
        """404 response must contain 'Not Found' message"""
        response = user_client.get_user("this-user-definitely-does-not-exist-xyz123abc")
        body = response.json()
        assert "message" in body
        assert "Not Found" in body["message"]

    @pytest.mark.parametrize("username", [
        "this-user-does-not-exist-aaa111",
        "fake-user-bbb222",
        "nonexistent-ccc333",
    ])
    def test_multiple_invalid_users_return_404(self, user_client, username):
        """Parametrized: multiple invalid usernames all return 404"""
        response = user_client.get_user(username)
        assert response.status_code == 404
