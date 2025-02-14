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


def get_most_recent_timestamp_and_schema_from_gcs(bucket_name: str, file_prefix: str) -> (datetime, dict[str, str]):
    """
    Retrieves the most recent timestamp and schema from a CSV file in a GCS bucket.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        file_prefix (str): The common prefix of filenames (e.g., "data/sales_"). Assumes timestamp is AFTER the prefix.
                              For example, if filenames are `data/sales_20231027_103000.csv`,
                              `file_prefix` would be `data/sales_`

    Returns:
        (datetime, dict[str, str]):
            - The most recent timestamp as a datetime object in UTC, or None if no matching files are found.
            - The schema of the most recent CSV file (column names and data types), or None if no file is found or an
                error occurs.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=file_prefix)

    timestamp_regex = re.compile(r"_(\d{8}_\d{6})\.")  # Matches _YYYYMMDD_HHMMSS
    most_recent_timestamp = None
    most_recent_blob_name = None
    most_recent_schema = None

    for blob in blobs:
        if not blob.name.endswith(".csv"):
            continue

        match = timestamp_regex.search(blob.name)
        if match:
            try:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                timestamp = timestamp.replace(tzinfo=timezone.utc)  # Convert to UTC

                if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                    most_recent_timestamp = timestamp
                    most_recent_blob_name = blob.name

            except ValueError as e:
                print(f"Error parsing timestamp from filename {blob.name}: {e}")

    if most_recent_blob_name:
        try:
            blob = bucket.blob(most_recent_blob_name)
            csv_data = blob.download_as_string().decode("utf-8")
            df = pd.read_csv(io.StringIO(csv_data))
            most_recent_schema = dict(df.dtypes)
            print(f"Schema extracted from most recent file: {most_recent_blob_name}")
        except Exception as e:
            print(f"Error loading data or extracting schema from {most_recent_blob_name}: {e}")
            most_recent_schema = None

    return most_recent_timestamp, most_recent_schema


def extend_dataframe_with_schema(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    """
    Extends a DataFrame with columns from a given schema that are missing in the DataFrame.
    New columns are filled with None/NaN values.

    Args:
        df (pd.DataFrame): The DataFrame to extend.
        schema (dict[str, str]): A dictionary where keys are column names and values are data types.

    Returns:
        pd.DataFrame: The extended DataFrame.
    """
    for col, dtype in schema.items():
        if col not in df.columns:
            df[col] = None

            try:  # Try to set the correct dtype
                if dtype == 'object':
                    df[col] = df[col].astype(str)
                elif dtype == 'int64':
                    df[col] = df[col].astype(int)
                elif dtype == 'float64':
                    df[col] = df[col].astype(float)
                elif dtype == 'bool':
                    df[col] = df[col].astype(bool)

            except Exception as e:
                print(f"Could not set dtype {dtype} for {col}: {e}")
    return df


def backfill_missing_columns(bucket_name: str, file_prefix: str, latest_schema: dict[str, str]):
    """
    Iterates through all CSV files in a GCS bucket with a given prefix and adds missing columns
    from the latest schema, filling the new columns with None/NaN.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        file_prefix (str): The prefix of the CSV files to process.
        latest_schema (dict[str, str]): The schema to use for backfilling, a dict where keys are column names and values are pandas data types.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=file_prefix)

    for blob in blobs:
        if not blob.name.endswith(".csv"):
            continue

        try:
            # Download the blob as a string and read into a DF
            csv_data = blob.download_as_string().decode("utf-8")
            df = pd.read_csv(io.StringIO(csv_data))

            # Extend the DataFrame with missing columns
            df = extend_dataframe_with_schema(df, latest_schema)

            # Save the updated DataFrame back to CSV
            updated_csv_data = df.to_csv(index=False)

            # Upload the updated CSV data back to the blob
            blob.upload_from_string(updated_csv_data, content_type="text/csv")

            print(f"Successfully backfilled missing columns for {blob.name}")

        except Exception as e:
            print(f"Error processing {blob.name}: {e}")


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
    start_time, latest_schema = get_most_recent_timestamp_and_schema_from_gcs(MONITORING_BUCKET, FILE_PREFIX)

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
        if 'id' not in tra.columns:
            raise Exception('ID column was not found in the fetched traces. Merging with fetched generations will fail')
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

        if latest_schema:
            # If current file does not contain some columns that the old one does, extend the current schema
            tra = extend_dataframe_with_schema(tra, latest_schema)

            # If necessary, iterate over all previous tables in the bucket and add them as null
            current_schema = dict(tra.dtypes)
            new_columns = set(current_schema.keys()) - set(latest_schema.keys())
            if new_columns:
                print(f"New columns {', '.join(list(new_columns)[:5])} detected in latest schema. Backfilling...")
                backfill_missing_columns(MONITORING_BUCKET, FILE_PREFIX, current_schema)

        # Define Filename
        timestamp_str = current_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{FILE_PREFIX}{timestamp_str}.csv"

        # Create CSV string in memory
        csv_string = tra.to_csv(index=False)

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
    result, status_code = export_from_langfuse(mock_request)
    print(f"Result: {result}, Status Code: {status_code}")
