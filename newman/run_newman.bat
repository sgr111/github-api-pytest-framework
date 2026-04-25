@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM run_newman.bat — Run GitHub API Postman collection via Newman CLI
REM Usage: newman\run_newman.bat
REM Requires: npm install -g newman newman-reporter-htmlextra
REM ─────────────────────────────────────────────────────────────────────────

echo.
echo =========================================
echo   GitHub API Newman Test Runner
echo   Author: Sourabh Sagar
echo =========================================
echo.

REM Create reports directory if it doesn't exist
if not exist "reports" mkdir reports

REM Set token from environment variable (set in .env or Jenkins)
REM Replace YOUR_TOKEN_HERE with actual token if running manually
set GITHUB_TOKEN=%GITHUB_TOKEN%

REM Run Newman with htmlextra reporter
newman run postman/GitHub_API_Collection.json ^
  --env-var "GITHUB_TOKEN=%GITHUB_TOKEN%" ^
  --reporters cli,htmlextra ^
  --reporter-htmlextra-export reports/newman-report.html ^
  --reporter-htmlextra-title "GitHub API Test Report" ^
  --reporter-htmlextra-browserTitle "GitHub API Tests" ^
  --reporter-htmlextra-darkTheme ^
  --delay-request 300

echo.
echo =========================================
echo   Newman run complete!
echo   Report: reports/newman-report.html
echo =========================================
