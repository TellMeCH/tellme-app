# CI/CD Setup

## Environments
* `develop (TELLME_ENV="dev")`: Local environment, running on the docker-compose.yml file at the root of the project
* `staging (TELLME_ENV="staging")`: Staging environment, running on a separate GCP Project
* `main (TELLME_ENV="prod")`: Production environment, running on another separate GCP Project


## Branch Organization
This project has the following branch types:
* `feature/*`: Feature branches, onboarding new functionalities
* `fix/*`: Fix branches, allowing quick resolution of bugs
* `develop`: Branch corresponding to the development environment. Whenever a PR to this branch is opened, a local testing workflow `ci_local.yml` will be triggered.
* `staging`: Branch corresponding to the staging environment. Whenever a PR to this branch is closed, a deployment and smoke test workflow `deploy.yml` will be triggered.
* `main`: Branch corresponding to the production environment. Whenever a PR to this branch is closed, a deployment and smoke test workflow `deploy.yml` will be triggered.

Code changes should flow through the branches in the following order:

`feature/*` >> `develop` >> `staging` >> `main`

Branch protection rules will not allow a different order.

## CI/CD Workflows
* `ci_local.yml`: Runs unit tests emulating the development environment with a local DB. These unit tests focus on all existing app views, their permissions, and expected outputs.
* `deploy.yml`: Contains two parts
  1. Deployment: Deploys to the environment of the target branch of the PR. Runs migrations if changes are detected in call_miner/migrations/. Connects to the target SQL DB with Google's Cloud SQL Proxy.
  2. Smoke Testing: Tests the deployed instance by simulating the creation of a new call recording. This is done both via a simple HTTP POST call as well as emulating a Genesys Audiohook connection that streams the call audio.
* `enforce_branch_rules.yml`: Implements the aforementioned branch protection rules as a check at every PR.