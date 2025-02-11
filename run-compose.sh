#!/usr/bin/env bash
#
# Usage:
#   ./run-compose.sh [--db-admin]
#
#   --db-admin:        Also fetch & append the 'database_admin' secret
#   --with-db-setup:   Run migrations + sample data at container startup

echo "Synchronizing .env file with secrets from GCP Secret Manager"
set -eu

FETCH_DB_ADMIN="false"
RUN_DB_SETUP="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db-admin)
      FETCH_DB_ADMIN="true"
      shift
      ;;
    --with-db-setup)
      RUN_DB_SETUP="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: ./run-compose.sh [--db-admin]"
      exit 1
      ;;
  esac
done

# Read existing .env for GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT
# Also "source" .env to have them in variables in this script.

if [[ ! -f .env ]]; then
  echo ".env file not found. Aborting."
  exit 1
fi

set -o allexport
source .env
set +o allexport

if [[ -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  echo "GOOGLE_CLOUD_PROJECT not set in .env. Aborting."
  exit 1
fi

if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
  echo "GOOGLE_APPLICATION_CREDENTIALS not set in .env. Aborting."
  exit 1
fi

# Use gcloud + the credentials to fetch django_settings from Secret Manager and append to .env
export GOOGLE_APPLICATION_CREDENTIALS
export CLOUDSDK_CORE_PROJECT="$GOOGLE_CLOUD_PROJECT"

DJA_PAYLOAD=$(gcloud secrets versions access latest \
  --secret="django_settings" \
  --project="$GOOGLE_CLOUD_PROJECT" 2>/dev/null || true)

if [[ -z "$DJA_PAYLOAD" ]]; then
  echo "Warning: 'django_settings' secret was not retrieved (possibly not found or no access)."
else
  # Append the payload lines to .env
  echo "" >> .env
  echo "# --- BEGIN django_settings secret lines ---" >> .env
  echo "$DJA_PAYLOAD" >> .env
  echo "# --- END django_settings secret lines ---" >> .env
fi

# Optionally fetch & append database_admin
DBA_PAYLOAD=""
if [[ "$FETCH_DB_ADMIN" == "true" ]]; then
  DBA_PAYLOAD=$(gcloud secrets versions access latest \
    --secret="database_admin" \
    --project="$GOOGLE_CLOUD_PROJECT" 2>/dev/null || true)

  if [[ -z "$DBA_PAYLOAD" ]]; then
    echo "Warning: 'database_admin' secret was not retrieved."
  else
    echo "" >> .env
    echo "# --- BEGIN database_admin secret lines ---" >> .env
    echo "$DBA_PAYLOAD" >> .env
    echo "# --- END database_admin secret lines ---" >> .env
  fi
fi

# The .env file is now updated and ready for Docker Compose to read
set -a
source .env
set +a

# Exporting RUN_DB_SETUP
export RUN_DB_SETUP

# If re-setting the DB, delete all previous volumes
if [[ "$RUN_DB_SETUP" == "true" ]]; then
  docker compose down -v
fi

# Run docker-compose up --build
docker-compose up --build

# Clean up the newly appended lines from .env if the user provided --remove-appended

# We'll remove the lines between the markers we inserted above:
# "# --- BEGIN django_settings secret lines ---" to "# --- END django_settings secret lines ---"
# "# --- BEGIN database_admin secret lines ---" to "# --- END database_admin secret lines ---"
# This approach simply filters out those lines, preserving the rest.
tmpfile=$(mktemp)
awk '
  /# --- BEGIN django_settings secret lines ---/ {removeBlock=1; next}
  /# --- END django_settings secret lines ---/   {removeBlock=0; next}
  /# --- BEGIN database_admin secret lines ---/  {removeBlockDB=1; next}
  /# --- END database_admin secret lines ---/    {removeBlockDB=0; next}
  removeBlock == 1 || removeBlockDB == 1 {next}
  {print}
' .env > "$tmpfile"

mv "$tmpfile" .env
