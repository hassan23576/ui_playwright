cat > Jenkinsfile << 'EOF'
pipeline {
  agent any

  // choose which batch to run when you click "Build with Parameters"
  parameters {
    choice(name: 'BATCH', choices: ['all','p1','p2'], description: 'Which batch to run')
  }

  // each build writes to its own folder so reports never clash
  environment {
    OUT_DIR = "artifacts/${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        // SSH URL (recommended). If private, set credentialsId to your Jenkins SSH key ID.
        // Replace <YOUR-USER> with your GitHub username.
        git branch: 'main',
            url: 'git@github.com:<YOUR-USER>/ui_playwright.git',
            credentialsId: 'github-ssh'  // remove this line if your repo is public
      }
    }

    stage('Setup') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install -U pip
          pip install -r requirements.txt
          python -m playwright install --with-deps
          mkdir -p "${OUT_DIR}"
        '''
      }
    }

    stage('Run Batches') {
      steps {
        sh '''
          . venv/bin/activate
          python scripts/run_batch.py --batch ${BATCH} --out "${OUT_DIR}"
        '''
      }
      post {
        always {
          // show test results in Jenkins UI
          junit "${OUT_DIR}/**/results_*.xml"
          // keep HTML reports and any other outputs
          archiveArtifacts artifacts: "${OUT_DIR}/**", fingerprint: true
        }
      }
    }

    stage('Summarize') {
      steps {
        sh '''
          . venv/bin/activate
          python scripts/parse_batches.py "${OUT_DIR}" > "${OUT_DIR}/summary.json"
          echo "===== SUMMARY ====="
          cat "${OUT_DIR}/summary.json"
        '''
      }
      post {
        always {
          archiveArtifacts artifacts: "${OUT_DIR}/summary.json", fingerprint: true
        }
      }
    }

    // Add a Confluence publish stage later if you want
    // stage('Publish to Confluence') { ... }
  }

  // Optional: run every Friday evening like CPI
  // triggers { cron('H 20 * * 5') }

  post {
    success { echo "✅ Done. Open Test Result + Artifacts tabs for reports." }
    failure { echo "❌ Failed. Check console, JUnit tab, and HTML reports." }
  }
}
EOF
