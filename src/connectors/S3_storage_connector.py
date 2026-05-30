import boto3
from botocore.exceptions import ClientError
from src.constants import (
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

if not AWS_ENDPOINT_URL or not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("As credenciais do S3 não foram encontradas no .env!")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    endpoint_url=AWS_ENDPOINT_URL
)

class S3StorageConnector:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = s3_client

    def upload_file(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type
        )
        return file_name

    def get_signed_url(self, file_name: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': file_name
            },
            ExpiresIn=expires_in
        )

    def delete_file(self, file_name: str) -> None:

        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=file_name
        )