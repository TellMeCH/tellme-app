import os
import io
import re
import environ
import langfuse
import pandas as pd
from google.cloud import storage
from google.cloud import secretmanager
from datetime import datetime, timedelta, timezone
from functions_framework import http

env = environ.Env()
SECRET_NAME = env('SETTINGS_NAME')
GOOGLE_CLOUD_PROJECT = env('GOOGLE_CLOUD_PROJECT')
MONITORING_BUCKET = f"{GOOGLE_CLOUD_PROJECT}_{os.getenv('MONITORING_BUCKET')}"
FILE_PREFIX = 'langfuse_data/langfuse_traces_'


def langfuse_observations_to_dataframe(langfuse_client: langfuse.Langfuse, start_time: datetime) -> pd.DataFrame:
    """
    Fetches Langfuse observations and converts them into a Pandas DataFrame.

    Args:
        langfuse_client (langfuse.Client): The Langfuse client object.
        start_time (datetime): The starting datetime (UTC) for fetching observations.

    Returns:
        pd.DataFrame: A DataFrame containing the Langfuse observations.  Returns an empty DataFrame if no data is found.
    """
    data = []
    page = 1
    while True:
        observations = langfuse_client.fetch_observations(from_start_time=start_time, limit=100, page=page)
        if observations.data:
            for item in observations.data:
                data.append(item.dict())
        page += 1
        if not observations.meta or not observations.meta.total_pages or page > observations.meta.total_pages:
            break
    return pd.DataFrame(data)


def langfuse_traces_to_dataframe(langfuse_client: langfuse.Langfuse, start_time: datetime) -> pd.DataFrame:
    """
    Fetches Langfuse traces and converts them into a Pandas DataFrame.

    Args:
        langfuse_client (langfuse.Client): The Langfuse client object.
        start_time (datetime): The starting datetime (UTC) for fetching traces.

    Returns:
        pd.DataFrame: A DataFrame containing the Langfuse traces. Returns an empty DataFrame if no data is found.
    """
    data = []
    page = 1
    while True:
        traces = langfuse_client.fetch_traces(from_timestamp=start_time, limit=100, page=page)
        if traces.data:
            for item in traces.data:
                data.append(item.dict())
        page += 1
        if not traces.meta or not traces.meta.total_pages or page > traces.meta.total_pages:
            break
    return pd.DataFrame(data)


def get_most_recent_timestamp_from_gcs(bucket_name: str, file_prefix: str) -> datetime | None:
    """
    Retrieves the most recent timestamp from filenames in a GCS bucket.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        file_prefix (str):  The common prefix of filenames (e.g., "data/sales_"). Assumes timestamp is AFTER the prefix.
                              For example, if filenames are `data/sales_20231027_103000.csv`,
                              `file_prefix` would be `data/sales_`

    Returns:
        datetime | None: The most recent timestamp as a datetime object,
                          or None if no matching files are found.  Returns in UTC.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=file_prefix)

    timestamp_regex = re.compile(r"_(\d{8}_\d{6})\.")  # Matches _YYYYMMDD_HHMMSS
    most_recent_timestamp = None
    for blob in blobs:
        match = timestamp_regex.search(blob.name)
        if match:
            try:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                timestamp = timestamp.replace(tzinfo=timezone.utc)  # Convert to UTC

                if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                    most_recent_timestamp = timestamp
            except ValueError as e:
                print(f"Error parsing timestamp from filename {blob.name}: {e}")
    return most_recent_timestamp


@http
def export_from_langfuse(request) -> (str, int):
    """
    Cloud Function to export data from Langfuse, process it, and upload it to Google Cloud Storage.

    Args:
        request (flask.Request): The request object. Not directly used, but required for Cloud Function execution.

    Returns:
        (str, int): A tuple containing the status message (e.g., "Success") and the HTTP status code (e.g., 200).
    """
    # Define the Execution and Load Start Times (All in UTC)
    current_time = datetime.now(timezone.utc)
    start_time = get_most_recent_timestamp_from_gcs(MONITORING_BUCKET, FILE_PREFIX)

    # Default start time if no files exist in GCS
    if not start_time:
        start_time = current_time - timedelta(days=1)

    print(f'Current Datetime: {current_time.isoformat()}')
    print(f'Fetching from: {start_time.isoformat()}')

    # Load Secrets
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/{SECRET_NAME}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    payload = response.payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))

    # Langfuse Client
    langfuse_client = langfuse.Langfuse(
      secret_key=env('LANGFUSE_SECRET_KEY'),
      public_key=env('LANGFUSE_PUBLIC_KEY'),
      host=env('LANGFUSE_HOST')
    )

    # Fetch Dataframes
    obs = langfuse_observations_to_dataframe(langfuse_client, start_time)
    tra = langfuse_traces_to_dataframe(langfuse_client, start_time)

    # Focusing on Generations - Process only if observations are present
    if not obs.empty:
        gen = obs.loc[obs['type'] == 'GENERATION'].copy()  # Avoid SettingWithCopyWarning
        gen.loc[:, 'failed'] = gen['statusMessage'].notna()

        # Reformatting the 'name' column
        gen.loc[gen['name'] == 'OpenAI-generation', 'name'] = gen.loc[gen['name'] == 'OpenAI-generation', 'promptName']
        gen.loc[gen['name'] == 'transcribe_chunk_with_groq', 'name'] = 'transcription_groq'

        # Aggregate by Trace ID and Name
        gens_agg = (
            gen
            .groupby(['traceId', 'name'])
            .agg(
                count=('id', 'size'),
                cost=('calculatedTotalCost', 'sum'),
                latency=('latency', lambda x: x.sum() / 1000),
                failed_count=('failed', lambda x: x.sum())
            )
            .reset_index()
        )

        # Pivot and Aggregate by Trace ID
        gens_agg = gens_agg.pivot_table(
            index='traceId',
            columns='name',
            values=['count', 'cost', 'latency', 'failed_count']
        )

        # Handle MultiIndex columns after pivot
        relevant_cols = [f'{val}_{col}' for val, col in gens_agg.columns]
        gens_agg.columns = relevant_cols
        gens_agg = gens_agg.reset_index()

        gens_agg = (
            gens_agg
            .groupby('traceId')
            .agg({col: 'sum' for col in relevant_cols})
            .reset_index()
            .rename(columns={'traceId': 'id'})
        )

        # Now Join with the original Traces Data
        tra = tra.merge(gens_agg, on='id', how='left')

    # Enrich Traces with execution status, environment, and if possible, call duration
    if not tra.empty:
        # Check if failed count columns exist before attempting to use them
        failed_count_cols = [c for c in tra.columns if 'failed_count' in c]
        if failed_count_cols:
            tra['failed'] = tra[failed_count_cols].any(axis=1)
        else:
            tra['failed'] = False
        tra['environment'] = tra['tags'].apply(lambda x: next(iter(x), None))
        tra['call_duration'] = tra['metadata'].apply(
            lambda x: x.get('total_duration_minutes') if isinstance(x, dict) and 'total_duration_minutes' in x else None
        )

        # Define Filename
        timestamp_str = current_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{FILE_PREFIX}{timestamp_str}.csv"

        # Create CSV string in memory
        csv_string = tra.to_csv(index=False)  # Pandas directly to CSV

        # Upload to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(MONITORING_BUCKET)
        blob = bucket.blob(filename)
        blob.upload_from_string(csv_string, content_type="text/csv")

        print(f"CSV file uploaded to gs://{MONITORING_BUCKET}{filename}")

    else:
        print("No traces data to enrich.")
    return "Success", 200


if __name__ == '__main__':
    class MockRequest:
        def get_json(self, silent=True):
            return {}
    mock_request = MockRequest()

    result, status_code = export_from_lanfuse(mock_request)
    print(f"Result: {result}, Status Code: {status_code}")
