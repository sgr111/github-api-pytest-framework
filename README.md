# GitHub API Pytest Framework

[![GitHub API Test Suite](https://github.com/sgr111/github-api-pytest-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/sgr111/github-api-pytest-framework/actions/workflows/ci.yml)

A production-grade, dual-layer API test automation framework built with **Python, Pytest, Requests, and Pydantic v2**, alongside a parallel **Postman/Newman** suite — testing the real **GitHub REST API** across **116 total assertions**. Implements a 3-stage CI/CD pipeline (GitHub Actions: smoke → regression → Newman) plus a Jenkins declarative pipeline, with automated HTML report generation on every run.

---

## Why This Project Exists

Most testing portfolios validate a toy/mock API. This framework instead tests a **real, live, third-party production API** (GitHub's), which means it has to deal with real-world constraints that mock APIs never surface: OAuth token scopes, rate limiting, authentication edge cases, and CI/CD credential management. Phase 4 of this project (see below) is a documented example of exactly that.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Test Framework | Pytest, pytest-html, pytest-xdist, Allure |
| HTTP Client | `requests` |
| Schema Validation | Pydantic v2 |
| Secondary Test Layer | Postman, Newman (CLI), newman-reporter-htmlextra |
| CI/CD | GitHub Actions (3-stage pipeline), Jenkins (5-stage declarative pipeline) |
| Language | Python 3.11 |

---

## Test Coverage

```
Total: 116 assertions
  ├── 72 Pytest tests
  └── 44 Newman (Postman) assertions

Suites:
  ├── test_auth.py     — authentication, rate limits, authenticated user profile
  ├── test_repos.py     — repository lookups, commits, issues, contributors, languages, branches
  ├── test_search.py    — repo search, user search, pagination, negative cases
  └── test_users.py     — user profiles, user repos, followers, negative/404 cases
```

Test types included: **smoke**, **regression**, **negative/error-path**, **schema validation**, **IDOR/security**, and **rate-limit** tests.

---

## Design Patterns & Architecture

### API Client Classes (Page-Object-Model equivalent for APIs)
Instead of Page Objects for UI, each GitHub resource gets a thin client class wrapping its endpoints, all sharing common assertion helpers from a base class:

```python
class BaseClient:
    def assert_status(self, response, expected): ...
    def assert_response_time(self, response, max_seconds): ...

class RepoClient(BaseClient):
    def get_repo(self, owner: str, repo: str):
        """GET /repos/{owner}/{repo}"""
        return self.get(f"/repos/{owner}/{repo}")

    def get_repo_commits(self, owner: str, repo: str, per_page: int = 10):
        """GET /repos/{owner}/{repo}/commits"""
        return self.get(f"/repos/{owner}/{repo}/commits", params={"per_page": per_page})
```

**Benefits:** reusable assertions, centralized auth header management, one place to update if the API changes.

### Pydantic v2 Data Contracts
Every response is parsed into a Pydantic model, so a breaking API change fails the test immediately instead of silently passing:

```python
class UserModel(BaseModel):
    login: str
    id: int
    type: str
    public_repos: int
    followers: int

    @field_validator("type")
    @classmethod
    def type_must_be_user_or_org(cls, v):
        assert v in ("User", "Organization"), f"Unexpected type: {v}"
        return v
```

### Session-Scoped Fixtures
API clients are instantiated once per test session, not once per test:

```python
@pytest.fixture(scope="session")
def repo_client():
    return RepoClient()
```

This avoids re-loading the token and rebuilding a client 72 times, and mirrors realistic HTTP connection reuse instead of a fresh session per test.

---

## Project Structure

```
github-api-pytest-framework/
├── .github/workflows/ci.yml     # 3-stage GitHub Actions pipeline
├── clients/                     # Thin API client wrappers per resource
│   ├── auth_client.py
│   ├── repo_client.py
│   ├── search_client.py
│   ├── user_client.py
│   └── base_client.py           # shared request/assert helpers
├── models/
│   └── github_models.py         # Pydantic v2 response schemas
├── tests/
│   ├── test_auth.py
│   ├── test_repos.py
│   ├── test_search.py
│   └── test_users.py
├── postman/
│   └── GitHub_API_Collection.json
├── newman/                      # Newman config/reports
├── conftest.py                  # shared fixtures
├── pytest.ini                   # markers: smoke, regression, negative
├── Jenkinsfile                  # 5-stage declarative Jenkins pipeline
├── requirements.txt
└── .env.example
```

---

## CI/CD Pipeline

**GitHub Actions** (`.github/workflows/ci.yml`) — runs on every push to `main`/`feature/*`/`fix/*`, on PRs to `main`, and daily on a schedule:

```
1. Smoke Tests       → fast subset (@pytest.mark.smoke), must pass first
2. Full Regression   → complete Pytest suite (needs: smoke-tests)
3. Newman Collection → Postman suite via CLI (needs: regression-tests)
```

Each stage uploads its HTML report as a workflow artifact regardless of pass/fail.

**Jenkins** (`Jenkinsfile`) — a parallel 5-stage declarative pipeline (checkout → Python setup → install → test execution → HTML report archival), scheduled daily, demonstrating familiarity with a self-hosted CI tool alongside GitHub Actions.

---

## Setup & Local Run

```bash
git clone https://github.com/sgr111/github-api-pytest-framework.git
cd github-api-pytest-framework

python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your own GitHub token — see "Authentication" below

pytest -v
```

### Running specific suites
```bash
pytest -m smoke          # fast smoke subset only
pytest -m regression     # full regression suite
pytest -m negative       # negative/error-path tests only
pytest --html=reports/report.html --self-contained-html   # generate HTML report
```

### Running the Postman suite locally
```bash
npm install -g newman newman-reporter-htmlextra
newman run postman/GitHub_API_Collection.json \
  --env-var "GITHUB_TOKEN=$GITHUB_TOKEN" \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export reports/newman-report.html
```

---

## Authentication

This framework authenticates against the real GitHub API, so it needs a token with the right scope — a plain, unscoped token is **not** enough for the `/user` endpoint.

**Locally:** create a [fine-grained personal access token](https://github.com/settings/tokens?type=beta) with:
- Repository access → your fork/copy of this repo
- Repository permissions → **Contents: Read**, **Metadata: Read**
- Account permissions → **Profile: Read** (or Read/Write, if that's the only tier offered)

Add it to `.env` as `GITHUB_TOKEN=<your token>`.

**In CI:** the token is stored as a GitHub Actions repository secret named `GH_API_TOKEN` (not `GITHUB_API_TOKEN` — GitHub reserves the `GITHUB_` prefix for its own secrets) and referenced in the workflow as `${{ secrets.GH_API_TOKEN }}`.

---

## Phase 4 — A Real Debugging Case Study

Two tests (`GET /user` status check and login-field check) originally passed locally but failed in CI with `403 Forbidden`. Root cause: GitHub Actions' default `github.token` intentionally excludes the `user` OAuth scope by design (least-privilege default), which the `/user` endpoint requires.

**Fix:** created a fine-grained PAT with explicit `Contents`, `Metadata`, and `Profile` scopes, stored it as a `GH_API_TOKEN` secret, and updated the workflow's three token references accordingly. Along the way this also surfaced a separate, unrelated `401 Bad credentials` failure locally, caused by an *old, expired* classic token still sitting in a local `.env` file — a good reminder that CI and local environments can drift independently even when the code itself hasn't changed.

Full write-up of every error encountered, root cause, and fix is documented separately as an interview-ready case study.

---

## Author

**Sourabh Sagar**
Lucknow, Uttar Pradesh, India
[github.com/sgr111](https://github.com/sgr111) · sgrsourabh111@gmail.com

Built as part of a self-taught transition into Backend Development / QA Automation (SDET) roles.
