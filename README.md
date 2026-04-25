# GitHub API Pytest Framework

A production-grade API test automation framework built with **Python, Pytest, Requests, and Pydantic v2** — testing the real GitHub REST API.

[![CI](https://github.com/YOUR_USERNAME/github-api-pytest-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/github-api-pytest-framework/actions)

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| `pytest` | Test runner & framework |
| `requests` | HTTP calls to GitHub API |
| `pydantic v2` | Response schema validation (data contracts) |
| `pytest-html` | HTML test reports |
| `python-dotenv` | Secure token management via `.env` |
| `allure-pytest` | Beautiful test dashboards |
| `pytest-xdist` | Parallel test execution |
| `GitHub Actions` | CI/CD — smoke → regression pipeline |

---

## Project Structure

```
github-api-pytest-framework/
├── clients/                  ← API Client Classes (POM equivalent for REST)
│   ├── base_client.py        ← Session, headers, shared assertions
│   ├── user_client.py        ← /users endpoints
│   ├── repo_client.py        ← /repos endpoints
│   ├── search_client.py      ← /search endpoints
│   └── auth_client.py        ← /user + /rate_limit endpoints
├── models/
│   └── github_models.py      ← Pydantic v2 response schemas
├── tests/
│   ├── test_users.py         ← 14 user endpoint tests
│   ├── test_repos.py         ← 14 repo endpoint tests
│   ├── test_search.py        ← 12 search endpoint tests
│   └── test_auth.py          ← 11 auth & rate limit tests
├── reports/                  ← Auto-generated HTML reports
├── conftest.py               ← Shared fixtures (clients, test data)
├── pytest.ini                ← Markers, addopts, testpaths
├── requirements.txt
└── .github/workflows/ci.yml  ← Smoke → Regression CI pipeline
```

---

## Setup & Run

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/github-api-pytest-framework.git
cd github-api-pytest-framework
pip install -r requirements.txt
```

### 2. Configure your GitHub token
```bash
cp .env.example .env
# Edit .env and add your token:
# GITHUB_TOKEN=ghp_your_personal_access_token
# GITHUB_USERNAME=your_github_username
```

> **Get a token:** GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained → Read-only public repos is enough.

### 3. Run tests

```bash
# Run full suite with HTML report
pytest

# Smoke tests only (fast, ~30 seconds)
pytest -m smoke

# Full regression
pytest -m regression

# Negative tests only
pytest -m negative

# Parallel execution (4 workers)
pytest -n 4

# With Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Test Coverage (51 tests total)

| File | Tests | Markers |
|------|-------|---------|
| `test_users.py` | 14 | smoke, regression, negative |
| `test_repos.py` | 14 | smoke, regression, negative |
| `test_search.py` | 12 | smoke, regression, negative |
| `test_auth.py` | 11 | smoke, regression, negative |

### What's tested:
- ✅ Status code assertions (200, 401, 404, 422)
- ✅ Response schema validation via Pydantic v2
- ✅ Response time assertions (< 3s per endpoint)
- ✅ Content-Type header validation
- ✅ Pagination (`per_page` enforcement)
- ✅ Parametrized negative tests (multiple invalid inputs)
- ✅ Auth token validation (valid vs invalid)
- ✅ Rate limit quota & schema checks
- ✅ Sort order verification (stars desc)
- ✅ Field-level data assertions (sha length, star counts, etc.)

---

## CI/CD Pipeline

GitHub Actions runs **two sequential jobs** on every push:

```
Push to GitHub
     │
     ▼
┌─────────────┐
│ Smoke Tests │  ← Runs first (~30s)
└──────┬──────┘
       │ Pass
       ▼
┌──────────────────┐
│ Full Regression  │  ← All 51 tests
└──────────────────┘
       │
       ▼
  HTML Report + Allure Results uploaded as artifacts
```

---

## Reports

After running tests, open the HTML report:
```bash
open reports/report.html
```

For Allure dashboard:
```bash
allure serve allure-results
```

---

## Author

**Sourabh Sagar** — [github.com/sgr111](https://github.com/sgr111)
