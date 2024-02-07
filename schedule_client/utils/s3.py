from base64 import b64encode
import io
import os

import boto3
import botocore
from django.utils.safestring import mark_safe


class ImageClient:
    """Handle interactions with AWS S3 bucket"""

    def __init__(self) -> None:
        self.BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
        self.ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
        self.SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.ACCESS_KEY,
            aws_secret_access_key=self.SECRET_ACCESS_KEY,
        )

    def get_image_object(self, s3_image_path: str) -> io.BytesIO:
        """Retrieve image bytes-like object from S3 bucket

        Args:
            s3_image_path (str): Relative location of S3 path

        Returns:
            io.BytesIO: Bytes-like object representing image
        """
        try:
            s3_response_object = self.client.get_object(
                Bucket=self.BUCKET_NAME, Key=s3_image_path
            )
            return s3_response_object["Body"].read()
        except Exception as err:
            print(f"Error retrieving image: {s3_image_path}")
            print(err)
            return None

    def get_image_tag(self, s3_image_path: str) -> str:
        try:
            image_bin = b64encode(self.get_image_object(s3_image_path)).decode("utf-8")
            return f'<img src="data:image;base64,{image_bin}" style="height:300px"/>'
        except Exception as err:
            print(err)
            return "(error retrieving image)"

    def confirm_image_object(self, s3_image_path: str) -> None:
        try:
            self.client.head_object(Bucket=self.BUCKET_NAME, Key=s3_image_path)
        except Exception as e:
            print(e)
            raise

    def close(self) -> None:
        self.client.close()
