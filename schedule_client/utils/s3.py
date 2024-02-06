import io
import os

import boto3
import botocore


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

    def confirm_image_object(self, s3_image_path: str) -> None:
        try:
            self.client.head_object(Bucket=self.BUCKET_NAME, Key=s3_image_path)
        except Exception as e:
            print(e)
            raise
        # except botocore.exceptions.ClientError as e:
        #     if e.response["Error"]["Code"] == "404":
        #         print(f"Key: '{full_image_path}' does not exist.")
        #     else:
        #         print(f"Something else went wrong:\n{e}")
        #     return False

    def close(self) -> None:
        self.client.close()
