# cloud_storage_config.py
from google.cloud import storage
import os

# --- Configuration ---
# Replace with your actual bucket name
BUCKET_NAME = "your-unique-bucket-name" 
# Replace with the local path to the file you want to upload (e.g., 'my_report.pdf')
LOCAL_FILE_TO_UPLOAD = "test_image.jpg"
# The name you want the file to have in the bucket (e.g., 'user_uploads/img101.jpg')
DESTINATION_BLOB_NAME = "images/uploaded_photo.jpg"
# The local path where you want the file to be saved after download
LOCAL_FILE_FOR_DOWNLOAD = "downloaded_file.jpg"
# ---------------------


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the GCS bucket."""
    
    # 1. Instantiate a client (authenticates automatically)
    storage_client = storage.Client()
    
    # 2. Get the target bucket object
    bucket = storage_client.bucket(bucket_name)
    
    # 3. Create a blob (object) name in the bucket
    blob = bucket.blob(destination_blob_name)

    print(f"Uploading {source_file_name} to {bucket_name}/{destination_blob_name}...")
    
    # 4. Upload the file from the local path
    blob.upload_from_filename(source_file_name)

    # Note: If your bucket is public, the public URL will be:
    # f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    
    print(
        f"✅ File {source_file_name} uploaded successfully as {destination_blob_name}."
    )
    

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the GCS bucket to a local file."""
    
    # 1. Instantiate a client (authenticates automatically)
    storage_client = storage.Client()

    # 2. Get the target bucket object
    bucket = storage_client.bucket(bucket_name)
    
    # 3. Construct a client-side representation of a blob
    blob = bucket.blob(source_blob_name)
    
    # 4. Download the blob to the specified local file path
    blob.download_to_filename(destination_file_name)

    print(
        f"⬇️ Blob {source_blob_name} downloaded from bucket {bucket_name} "
        f"to local file {destination_file_name}."
    )


if __name__ == "__main__":
    # --- Example Usage ---
    
    # Ensure a dummy file exists for the upload test
    if not os.path.exists(LOCAL_FILE_TO_UPLOAD):
        with open(LOCAL_FILE_TO_UPLOAD, 'w') as f:
            f.write("This is a test file for GCS upload.")
            
    # 1. UPLOAD
    try:
        upload_blob(BUCKET_NAME, LOCAL_FILE_TO_UPLOAD, DESTINATION_BLOB_NAME)
    except Exception as e:
        print(f"Upload failed. Check your BUCKET_NAME and credentials. Error: {e}")
        
    print("-" * 30)

    # 2. DOWNLOAD
    # We download the file we just uploaded, but save it with a different local name
    # to demonstrate the process.
    try:
        download_blob(BUCKET_NAME, DESTINATION_BLOB_NAME, LOCAL_FILE_FOR_DOWNLOAD)
    except Exception as e:
        print(f"Download failed. Check the blob/file name and permissions. Error: {e}")