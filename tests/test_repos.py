"""
test_repos.py — Tests for GitHub /repos endpoints.

Covers: repo metadata, issues, commits, contributors,
        languages, branches, schema validation.
"""

import pytest
from models import RepoModel, CommitModel


@pytest.mark.smoke
@pytest.mark.repos
class TestRepoPositive:

    def test_get_known_repo_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo} returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo(owner, repo)
        repo_client.assert_status(response, 200)

    def test_get_known_repo_schema_valid(self, validated_repo):
        """Response matches RepoModel Pydantic schema"""
        assert isinstance(validated_repo, RepoModel)

    def test_get_known_repo_name_matches(self, validated_repo, known_repo):
        """name field in response matches requested repo name"""
        _, repo_name = known_repo
        assert validated_repo.name == repo_name

    def test_get_known_repo_not_private(self, validated_repo):
        """Public repo must have private=False"""
        assert validated_repo.private is False

    def test_get_known_repo_has_stars(self, validated_repo):
        """requests library must have significant stars"""
        assert validated_repo.stargazers_count > 1000

    def test_get_known_repo_default_branch_exists(self, validated_repo):
        """default_branch must be a non-empty string"""
        assert validated_repo.default_branch != ""

    def test_get_known_repo_content_type_json(self, repo_client, known_repo):
        """Content-Type must be application/json"""
        owner, repo = known_repo
        response = repo_client.get_repo(owner, repo)
        repo_client.assert_content_type_json(response)

    def test_get_known_repo_response_time(self, repo_client, known_repo):
        """Response must arrive within 3 seconds"""
        owner, repo = known_repo
        response = repo_client.get_repo(owner, repo)
        repo_client.assert_response_time(response, 3.0)


@pytest.mark.regression
@pytest.mark.repos
class TestRepoCommits:

    def test_get_commits_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo}/commits returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo_commits(owner, repo)
        repo_client.assert_status(response, 200)

    def test_get_commits_returns_list(self, repo_client, known_repo):
        """Commits response must be a list"""
        owner, repo = known_repo
        response = repo_client.get_repo_commits(owner, repo)
        assert isinstance(response.json(), list)

    def test_get_commits_schema_valid(self, repo_client, known_repo):
        """Each commit must match CommitModel Pydantic schema"""
        owner, repo = known_repo
        commits = repo_client.get_and_validate_commits(owner, repo)
        assert all(isinstance(c, CommitModel) for c in commits)

    def test_get_commits_each_has_sha(self, repo_client, known_repo):
        """Every commit must have a sha field"""
        owner, repo = known_repo
        response = repo_client.get_repo_commits(owner, repo, per_page=5)
        commits = response.json()
        assert all("sha" in c for c in commits)

    def test_get_commits_sha_length(self, repo_client, known_repo):
        """SHA must be 40 characters (full git hash)"""
        owner, repo = known_repo
        response = repo_client.get_repo_commits(owner, repo, per_page=5)
        commits = response.json()
        assert all(len(c["sha"]) == 40 for c in commits)


@pytest.mark.regression
@pytest.mark.repos
class TestRepoExtras:

    def test_get_repo_issues_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo}/issues returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo_issues(owner, repo)
        repo_client.assert_status(response, 200)

    def test_get_repo_contributors_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo}/contributors returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo_contributors(owner, repo)
        repo_client.assert_status(response, 200)

    def test_get_repo_languages_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo}/languages returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo_languages(owner, repo)
        repo_client.assert_status(response, 200)

    def test_get_repo_languages_python_present(self, repo_client, known_repo):
        """requests library must show Python as a language"""
        owner, repo = known_repo
        response = repo_client.get_repo_languages(owner, repo)
        languages = response.json()
        assert "Python" in languages

    def test_get_repo_branches_status_200(self, repo_client, known_repo):
        """GET /repos/{owner}/{repo}/branches returns 200"""
        owner, repo = known_repo
        response = repo_client.get_repo_branches(owner, repo)
        repo_client.assert_status(response, 200)


@pytest.mark.negative
@pytest.mark.repos
class TestRepoNegative:

    def test_get_nonexistent_repo_returns_404(self, repo_client):
        """GET /repos/{owner}/{nonexistent} must return 404"""
        response = repo_client.get_repo("torvalds", "this-repo-does-not-exist-xyz999")
        repo_client.assert_status(response, 404)

    @pytest.mark.parametrize("owner,repo", [
        ("fake-owner-111", "fake-repo-aaa"),
        ("fake-owner-222", "fake-repo-bbb"),
    ])
    def test_multiple_invalid_repos_return_404(self, repo_client, owner, repo):
        """Parametrized: multiple invalid repos all return 404"""
        response = repo_client.get_repo(owner, repo)
        assert response.status_code == 404
