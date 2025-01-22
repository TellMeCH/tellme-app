# TellMe
The right call to know your customer.

---

## Table of Contents
1. Project Description
2. Prerequisites
3. Installation
4. Usage
5. Features
6. Testing
7. Project Structure

---

## Project Description
Explain the purpose of your application, key features, and target audience.
TellMe aims to help companies understand their customer base by analyzing customer center calls.
Using AI, call recordings are transcribed, clustered, and summarized, to provide insights at the level of the company, the customer, or the topic cluster.
This application provides endpoints to serve this data according to different user roles, as well as the routines for processing every call and storing its results.
Its CI/CD is designed to deploy the application to GCP's Cloud Run, where a frontend will be able to reach it.
---

## Prerequisites for Local Execution
- Docker
- Docker Compose
- gcloud CLI
- Authenticated Access to the app's GCP project

---

## Usage in Local Setup
1. Authenticate to app's GCP project with the following bash commands. Take note of where the application default credentials are stored.
```bash
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
```
2. Create a simple .env file with the following variables:
   * GOOGLE_CLOUD_PROJECT : Use the app's GCP project
   * GOOGLE_APPLICATION_CREDENTIALS: Use the credential location defined in step 1. 
3. Ask the development team for the remaining .env variables and append them to your .env
4. Run the following to start the local environment, run migrations, and create sample data for experimentation
```bash
./run-compose.sh --with-db-setup
```
5. Enjoy!
6. Make sure you stop the local environment normally, using Ctrl+C. Moreover, for subsequent executions, avoid running migrations and run:
```bash
./run-compose.sh
```


## Features


---

## Testing
For local testing, proceed as follows:
1. Create a poetry environment has been created with the required packages (see pyproject.toml)
2. Run the local instance of the application (see above)
3. In a new terminal, import .env as follows:
   ```bash
   set -a; source .env; set +a;
   ```
4. Set DATABASE_HOST and FIREBASE_AUTH_EMULATOR_HOST as follows:
   ```bash
   export DATABASE_HOST=localhost; export FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099;
   ```
5. Finally, run the following:
    ```bash
    poetry run pytest -v --ignore=./call_processing/tests/test_smoke_remote.py
    ```

---

## Project Structure
The Django project is separated into two apps:
- call_miner: Aimed at serving the DBs data to a frontend. Serves as a REST API providing call data to relevant users.
- call_processing: Contains the processing routine through which every call goes.

<project-root>/
├── Dockerfile
├── README.md
├── call_miner
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── authentication_extensions.py
│   ├── forms.py
│   ├── management
│   │   ├── __init__.py
│   │   └── commands
│   │       ├── __init__.py
│   │       ├── create_sample_data.py
│   │       └── create_superusers.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── postman_generator.py
│   ├── schemas.py
│   ├── serializers.py
│   ├── templates
│   │   └── call_detail.html
│   ├── tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_agents.py
│   │   ├── test_conversations.py
│   │   ├── test_customers.py
│   │   ├── test_employees.py
│   │   ├── test_models.py
│   │   ├── test_organization_api_keys.py
│   │   ├── test_organizations.py
│   │   ├── test_summary_mining.py
│   │   └── test_topics.py
│   ├── urls.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── fallback_prompt.py
│   │   ├── paginators.py
│   │   └── summary_mining.py
│   └── views.py
├── call_processing
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── authentication_extensions.py
│   ├── consumers.py
│   ├── migrations
│   │   ├── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_call_processing.py
│   │   ├── test_process.py
│   │   ├── test_queue.py
│   │   └── test_smoke_remote.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── call_processing.py
│   │   ├── db_handler.py
│   │   ├── fallback_prompt.py
│   │   └── gcs_utils.py
│   └── views.py
├── data
│   └── sample_recording.wav
├── docker-compose.yml
├── firebase-emulator
├── genesys_audiohook_emulator
├── manage.py
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── run-compose.sh
├── static
└── tell_me
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py


