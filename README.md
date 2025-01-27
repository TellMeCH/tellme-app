# TellMe
The right call to know your customers.

---

## Project Description
TellMe aims to help companies understand their customer base by analyzing customer center calls.
Using AI, call recordings are transcribed, clustered, and summarized, to provide insights at the level of the company, the customer, or the topic cluster.
This application provides endpoints to serve this data according to different user roles, as well as the routines for processing every call and storing its results.
Its CI/CD is designed to deploy the application to GCP's Cloud Run, where a frontend will be able to reach it.
---

## Local Execution

### Prerequisites:
- Docker
- Docker Compose
- gcloud CLI
- Authenticated Access to the app's GCP project

### Steps:
1. Authenticate to app's GCP project with the following bash commands. Take note of where the application default credentials are stored.
```bash
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
```
2. Create a simple .env file with the following variables:
   * `GOOGLE_CLOUD_PROJECT` : Use the app's GCP project
   * `GOOGLE_APPLICATION_CREDENTIALS`: Use the credential location defined in step 1. 
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

---

## Testing
For local testing, proceed as follows:
1. Create a poetry environment has been created with the required packages (see pyproject.toml)
2. Run the local instance of the application (see above)
3. In a new terminal, import .env as follows:
   ```bash
   set -a; source .env; set +a;
   ```
4. Set `DATABASE_HOST` and `FIREBASE_AUTH_EMULATOR_HOST` as follows:
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
### call_miner 
Aimed at serving the DBs data to a frontend. Serves as a REST API providing call data to relevant users. This app's structure revolves around its data model, which consists of:
  - **Organizations:** Entities using the product, each serving as an isolated container for DB access
  - **Topics:** Semantic labels associated to a call
  - **Customers:** Represents an organization's customer involved in a call recording
  - **User:** An account with access to the application
  - **Employee:** A user associated to a specific Organization
  - **Analysts and Agents:** Types of employee instances, with different functions. Analysts are user accounts that can access the DB but are not involved in its data. Agents, on the other hand, appear as participants in Conversations.
  - **Conversations:** Data point representing a call recording, associated to an agent, a customer, and zero or many topics 
### call_processing
Contains the processing routine through which every call goes. A bit more about this routine:
  1. Calls are transcribed 
  2. Using AI, calls are associated to one or more relevant topics based on the call content and the topic descriptions. 
  3. Also using AI, we obtain the probability of customer churn in a scale from 1 to 5, 1 being a customer who will certainly never interact with the company again, and 5 being a customer that is completely satisfied with the product or service in question. This is a proxy of the call sentiment. 
  4. With AI, a summary of each call is produced 
  5. Furthermore, call recordings of all the calls belonging to a single topic are aggregated and analyzed, to obtain the following:
     - Reasons for Calling 
     - Stages of the Customer Journey 
     - Call Resolution Rates
     - Churn Potential
     - Causes for Dissatisfaction
     - Causes for Engagement
     - Suggested Actions
