import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
ACCESS_KEY = os.getenv('R2_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('R2_BUCKET_NAME')

def get_r2_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name='auto'
    )


def upload_file(file_path, object_name):
    """Upload file ke R2"""
    r2 = get_r2_client()
    try:
        print(f"Mengupload {file_path}...")
        r2.upload_file(file_path, BUCKET_NAME, object_name)
        print("Upload berhasil!")
    except ClientError as e:
        print(f"Error upload: {e}")

def list_files():
    """List semua file di bucket"""
    r2 = get_r2_client()
    try:
        response = r2.list_objects_v2(Bucket=BUCKET_NAME)
        print("\nIsi Bucket:")
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"- {obj['Key']} (Ukuran: {obj['Size']} bytes)")
        else:
            print("Bucket kosong.")
    except ClientError as e:
        print(f"Error listing: {e}")

def download_file(object_name, download_path):
    """Download file dari R2"""
    r2 = get_r2_client()
    try:
        print(f"\nMendownload {object_name} ke {download_path}...")
        r2.download_file(BUCKET_NAME, object_name, download_path)
        print("Download berhasil!")
    except ClientError as e:
        print(f"Error download: {e}")

def generate_presigned_url(object_name, expiration=3600):
    """
    Membuat URL sementara agar orang lain bisa akses file private
    Expiration dalam detik (3600 = 1 jam)
    """
    r2 = get_r2_client()
    try:
        url = r2.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating URL: {e}")
        return None

if __name__ == "__main__":
    with open("test.txt", "w") as f:
        f.write("Hello, World!")

    upload_file("test.txt", "experiment/test-upload.txt")

    list_files()

    link = generate_presigned_url("experiment/test-upload.txt")
    print(f"\nLink sementara (berlaku 1 jam):\n{link}")

    download_file("experiment/test-upload.txt", "downloaded_test.txt")
    
    os.remove("test.txt")