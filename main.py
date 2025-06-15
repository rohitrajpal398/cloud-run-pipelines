import json
from google.cloud import bigquery

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

    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()

    print(f"Loaded data from {uri} into {table_ref}")

if __name__ == "__main__":
    config = load_config()
    load_data(config)
