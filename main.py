import json
import requests
from google.cloud import bigquery

# Replace this with your actual Google Chat webhook URL
GOOGLE_CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAfqvFgcM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=nRjJBvARoVb6-G5MRUr_sexB5NCGaSFpQHp73FRi-W0"

def send_google_chat_alert(message):
    payload = {"text": message}
    try:
        response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send alert to Google Chat: {e}")

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def load_data(config):
    client = bigquery.Client(project=config["project_id"])

    uri = f"gs://{config['gcs_bucket']}/{config['gcs_file']}"
    table_ref = f"{config['project_id']}.{config['bq_dataset']}.{config['bq_table']}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
        skip_leading_rows=1,
        write_disposition="WRITE_APPEND"
    )

    try:
        load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
        load_job.result()
        print(f"✅ Loaded data from {uri} into {table_ref}")
    except Exception as e:
        error_message = f"❌ Cloud Run Job Failed: Error loading data from GCS to BigQuery\n\n{str(e)}"
        print(error_message)
        send_google_chat_alert(error_message)
        raise  # re-raise the exception if needed for further logging or retries

if __name__ == "__main__":
    try:
        config = load_config()
        load_data(config)
    except Exception as e:
        # Optional: alert here as well if config loading fails
        send_google_chat_alert(f"❌ Cloud Run Job Failed during setup: {str(e)}")
        raise
