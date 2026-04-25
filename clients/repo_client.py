"""
Repo API Client — wraps all GitHub /repos endpoints.
"""

from .base_client import BaseClient
from models import RepoModel, IssueModel, CommitModel


class RepoClient(BaseClient):

    def get_repo(self, owner: str, repo: str):
        """GET /repos/{owner}/{repo}"""
        return self.get(f"/repos/{owner}/{repo}")

    def get_repo_issues(self, owner: str, repo: str, state: str = "open", per_page: int = 10):
        """GET /repos/{owner}/{repo}/issues"""
        return self.get(f"/repos/{owner}/{repo}/issues", params={
            "state": state,
            "per_page": per_page
        })

    def get_repo_commits(self, owner: str, repo: str, per_page: int = 10):
        """GET /repos/{owner}/{repo}/commits"""
        return self.get(f"/repos/{owner}/{repo}/commits", params={"per_page": per_page})

    def get_repo_contributors(self, owner: str, repo: str, per_page: int = 10):
        """GET /repos/{owner}/{repo}/contributors"""
        return self.get(f"/repos/{owner}/{repo}/contributors", params={"per_page": per_page})

    def get_repo_languages(self, owner: str, repo: str):
        """GET /repos/{owner}/{repo}/languages"""
        return self.get(f"/repos/{owner}/{repo}/languages")

    def get_repo_branches(self, owner: str, repo: str):
        """GET /repos/{owner}/{repo}/branches"""
        return self.get(f"/repos/{owner}/{repo}/branches")

    def get_and_validate_repo(self, owner: str, repo: str) -> RepoModel:
        """Fetch repo and validate schema with Pydantic"""
        response = self.get_repo(owner, repo)
        self.assert_status(response, 200)
        return RepoModel(**response.json())

    def get_and_validate_commits(self, owner: str, repo: str) -> list[CommitModel]:
        """Fetch commits and validate each with Pydantic"""
        response = self.get_repo_commits(owner, repo)
        self.assert_status(response, 200)
        return [CommitModel(**c) for c in response.json()]
