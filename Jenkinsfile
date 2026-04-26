// ---------------------------------------------------------------------------
// Jenkinsfile — ACEest Fitness & Gym — Declarative Pipeline
// ---------------------------------------------------------------------------
// This pipeline is configured to be triggered by a Jenkins project that
// pulls the latest code from GitHub and performs a clean build.
// ---------------------------------------------------------------------------

pipeline {
    agent any

    environment {
        APP_NAME    = 'aceest-fitness'
        PYTHON_VER  = '3.12'
        SCANNER_HOME = tool 'SonarQubeScanner'
    }

    triggers {
        pollSCM('H/5 * * * *')   // Poll GitHub every 5 minutes for changes
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo '🐍 Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '🔍 Running flake8 linter...'
                sh '''
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('SonarCloud Analysis') {
            steps {
                echo '📊 Running SonarCloud static code analysis...'
                withSonarQubeEnv('SonarCloud') {
                    sh "${SCANNER_HOME}/bin/sonar-scanner"
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo '🚦 Waiting for SonarCloud Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo '🧪 Running Pytest suite...'
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh "docker build -t ${APP_NAME}:${BUILD_NUMBER} ."
                sh "docker build -t ${APP_NAME}:latest ."
            }
        }

        stage('Container Test') {
            steps {
                echo '🧪 Running tests inside Docker container...'
                sh "docker run --rm ${APP_NAME}:latest python -m pytest test_app.py -v --tb=short"
            }
        }
    }

    post {
        success {
            echo '✅ BUILD SUCCESSFUL — All stages passed.'
        }
        failure {
            echo '❌ BUILD FAILED — Check the logs above for details.'
        }
        always {
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
    }
}
