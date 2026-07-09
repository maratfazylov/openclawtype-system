# Jenkins Pipeline Setup

## Recommended Job Type

Use a Pipeline job or Multibranch Pipeline job. For this prototype, a simple
Pipeline job is easiest to demo:

1. Create a new Jenkins item.
2. Choose `Pipeline`.
3. Enable `This project is parameterized`.
4. Add a boolean or string parameter named `OPENCLAW_SMOKE`.
5. In `Build Triggers`, enable `Trigger builds remotely` and set a job token,
   or use Jenkins API credentials through `JENKINS_USERNAME` and
   `JENKINS_API_TOKEN`.
6. Put the pipeline script below into the job, or point the job at a repository
   `Jenkinsfile`.

## Minimal Demo Jenkinsfile

```groovy
pipeline {
  agent any

  parameters {
    string(name: 'OPENCLAW_SMOKE', defaultValue: 'false', description: 'Run OpenClaw smoke path')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install') {
      steps {
        sh 'uv sync'
      }
    }

    stage('Test') {
      steps {
        sh 'uv run pytest --junitxml=pytest-report.xml'
      }
    }

    stage('OpenClaw Smoke') {
      when {
        expression { params.OPENCLAW_SMOKE == 'true' }
      }
      steps {
        sh '''
          uv run python -c "import agent; print(type(agent.agent).__name__); print(type(agent.swe_agent).__name__)"
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'pytest-report.xml', allowEmptyArchive: true
    }
  }
}
```

If the Jenkins agent does not have `uv`, install it on the node image or replace
the commands with the environment manager used by that Jenkins installation.

## Environment Variables For OpenClaw

Set these locally in `.env` before running the notebook:

```bash
JENKINS_JOB_URL=https://your-jenkins.example/job/openclaw-smoke/
JENKINS_JOB_TOKEN=...
OPENCLAW_RUN_REAL_JENKINS_PIPELINE=1
```

Keep `OPENCLAW_RUN_REAL_JENKINS_PIPELINE=0` until the dry-run and job metadata
checks pass. The connector can validate local configuration without network
access, but real metadata/build calls require the machine to reach the Jenkins
portal over HTTPS.

Or use API credentials instead of a job token:

```bash
JENKINS_USERNAME=...
JENKINS_API_TOKEN=...
OPENCLAW_RUN_REAL_JENKINS_PIPELINE=1
```

## Demo Flow

1. Run notebook cells through the dry-run preview.
2. Read job metadata.
3. Set `OPENCLAW_RUN_REAL_JENKINS_PIPELINE=1`.
4. Trigger the real pipeline.
5. Wait for queue resolution and final build status.

## Network Check

Before a live demo, verify that the Jenkins portal is reachable from the same
machine that runs the notebook:

```bash
curl -I --max-time 15 https://devops.brojs.ru/job/marat/
```

If this times out during TLS/connection setup, fix network/VPN/firewall access
first. Jenkins credentials cannot help until the host is reachable.

For a live presentation, keep the Jenkins job small. The pipeline should finish
in under two minutes, otherwise the audience watches Jenkins instead of the
agent architecture.
