from google.cloud import storage
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(r"D:\secrets\f1-pipeline-key.json")
client = storage.Client(project="f1-analytics-pipeline", credentials=creds)

bucket = client.bucket("f1-analytics-pipeline-raw")
for blob in bucket.list_blobs():
    print(blob.name)
