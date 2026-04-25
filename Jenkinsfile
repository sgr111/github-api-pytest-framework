pipeline {
    agent any

    environment {
        GITHUB_TOKEN = credentials('GITHUB_TOKEN')
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        // Run every day at 9AM
        cron('0 9 * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Pulling latest code from GitHub ==='
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                echo '=== Setting up Python virtual environment ==='
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Pytest - Smoke Tests') {
            steps {
                echo '=== Running Pytest Smoke Tests ==='
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest -m smoke ^
                        --html=reports/jenkins-smoke-report.html ^
                        --self-contained-html ^
                        -v
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'jenkins-smoke-report.html',
                        reportName: 'Pytest Smoke Report'
                    ])
                }
            }
        }

        stage('Pytest - Full Regression') {
            steps {
                echo '=== Running Full Pytest Regression Suite ==='
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest ^
                        --html=reports/jenkins-regression-report.html ^
                        --self-contained-html ^
                        -v
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'jenkins-regression-report.html',
                        reportName: 'Pytest Regression Report'
                    ])
                }
            }
        }

        stage('Newman - Postman Collection') {
            steps {
                echo '=== Running Postman Collection via Newman ==='
                bat '''
                    if not exist reports mkdir reports
                    newman run postman/GitHub_API_Collection.json ^
                        --env-var "GITHUB_TOKEN=%GITHUB_TOKEN%" ^
                        --reporters cli,htmlextra ^
                        --reporter-htmlextra-export reports/newman-report.html ^
                        --reporter-htmlextra-title "GitHub API Newman Report" ^
                        --reporter-htmlextra-darkTheme ^
                        --delay-request 300
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'newman-report.html',
                        reportName: 'Newman Postman Report'
                    ])
                }
            }
        }
    }

    post {
        success {
            echo '=== All stages passed! Pytest + Newman green ==='
        }
        failure {
            echo '=== Pipeline failed — check report artifacts above ==='
        }
        always {
            echo '=== Pipeline complete ==='
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }
    }
}
