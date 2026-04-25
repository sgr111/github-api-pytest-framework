"""
Pydantic v2 response models for GitHub API schema validation.
These act as data contracts — if GitHub changes its response shape,
our tests will catch it immediately.
"""

from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


class UserModel(BaseModel):
    """Schema for GET /users/{username}"""
    login: str
    id: int
    avatar_url: str
    html_url: str
    type: str
    public_repos: int
    followers: int
    following: int
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_must_be_user_or_org(cls, v):
        assert v in ("User", "Organization"), f"Unexpected type: {v}"
        return v


class RepoModel(BaseModel):
    """Schema for a single repo object"""
    id: int
    name: str
    full_name: str
    private: bool
    html_url: str
    description: Optional[str] = None
    fork: bool
    language: Optional[str] = None
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    default_branch: str


class SearchRepoResultModel(BaseModel):
    """Schema for GET /search/repositories"""
    total_count: int
    incomplete_results: bool
    items: list[RepoModel]

    @field_validator("total_count")
    @classmethod
    def total_count_non_negative(cls, v):
        assert v >= 0, "total_count must be non-negative"
        return v


class SearchUserItemModel(BaseModel):
    """Schema for a single user in search results"""
    login: str
    id: int
    avatar_url: str
    html_url: str
    type: str
    score: float


class SearchUserResultModel(BaseModel):
    """Schema for GET /search/users"""
    total_count: int
    incomplete_results: bool
    items: list[SearchUserItemModel]


class IssueModel(BaseModel):
    """Schema for a single issue object"""
    id: int
    number: int
    title: str
    state: str
    html_url: str
    user: dict
    body: Optional[str] = None

    @field_validator("state")
    @classmethod
    def state_must_be_valid(cls, v):
        assert v in ("open", "closed"), f"Unexpected state: {v}"
        return v


class CommitAuthorModel(BaseModel):
    name: str
    email: str
    date: str


class CommitDetailModel(BaseModel):
    message: str
    author: CommitAuthorModel


class CommitModel(BaseModel):
    """Schema for a single commit object"""
    sha: str
    commit: CommitDetailModel
    html_url: str


class RateLimitResourceModel(BaseModel):
    limit: int
    remaining: int
    reset: int
    used: int


class RateLimitModel(BaseModel):
    """Schema for GET /rate_limit"""
    resources: dict
    rate: RateLimitResourceModel
