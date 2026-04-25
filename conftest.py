"""
conftest.py — Shared fixtures for all tests.

Fixtures here are auto-available to every test file
without importing — pytest discovers them automatically.
"""

import pytest
import os
from dotenv import load_dotenv
from clients import UserClient, RepoClient, SearchClient, AuthClient

load_dotenv()

# ── Public well-known accounts used as stable test data ──────────────────────
KNOWN_USER = "torvalds"           # Linus Torvalds — very stable public profile
KNOWN_ORG = "python"              # Python org — stable
KNOWN_REPO_OWNER = "psf"         # Python Software Foundation
KNOWN_REPO_NAME = "requests"     # The 'requests' library — famous, stable repo
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")


# ── Client Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def user_client():
    """Session-scoped UserClient — one instance for entire test run"""
    return UserClient()


@pytest.fixture(scope="session")
def repo_client():
    """Session-scoped RepoClient"""
    return RepoClient()


@pytest.fixture(scope="session")
def search_client():
    """Session-scoped SearchClient"""
    return SearchClient()


@pytest.fixture(scope="session")
def auth_client():
    """Session-scoped AuthClient"""
    return AuthClient()


# ── Data Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def known_user():
    return KNOWN_USER


@pytest.fixture(scope="session")
def known_repo():
    return (KNOWN_REPO_OWNER, KNOWN_REPO_NAME)


@pytest.fixture(scope="session")
def github_username():
    return GITHUB_USERNAME


@pytest.fixture(scope="session")
def validated_user(user_client):
    """Pre-fetched & Pydantic-validated user — reused across tests"""
    return user_client.get_and_validate_user(KNOWN_USER)


@pytest.fixture(scope="session")
def validated_repo(repo_client):
    """Pre-fetched & Pydantic-validated repo — reused across tests"""
    return repo_client.get_and_validate_repo(KNOWN_REPO_OWNER, KNOWN_REPO_NAME)
