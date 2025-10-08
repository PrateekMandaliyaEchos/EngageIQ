#!/usr/bin/env python3
"""
Script to upload local data files to S3 for production deployment.
"""

import boto3
import os
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError


def upload_file_to_s3(s3_client, bucket_name, local_file_path, s3_key):
    """Upload a file to S3."""
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"✅ Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")
        return True
    except ClientError as e:
        print(f"❌ Error uploading {local_file_path}: {e}")
        return False


def main():
    """Upload data files to S3."""
    # Configuration
    bucket_name = "engageiq-data-prod"  # Change this to your bucket name
    s3_prefix = "campaign-data/"
    
    # Files to upload
    data_files = [
        "data/Agent_persona.csv",
        "data/campaigns.csv"
    ]
    
    # Initialize S3 client
    try:
        s3_client = boto3.client('s3')
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return
    
    # Check if bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket {bucket_name} exists")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"❌ Bucket {bucket_name} does not exist. Please create it first.")
            return
        else:
            print(f"❌ Error accessing bucket {bucket_name}: {e}")
            return
    
    # Upload files
    success_count = 0
    for file_path in data_files:
        if Path(file_path).exists():
            s3_key = s3_prefix + Path(file_path).name
            if upload_file_to_s3(s3_client, bucket_name, file_path, s3_key):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Upload complete: {success_count}/{len(data_files)} files uploaded successfully")
    
    if success_count == len(data_files):
        print("🎉 All files uploaded successfully! Your app is ready for production.")
    else:
        print("⚠️  Some files failed to upload. Please check the errors above.")


if __name__ == "__main__":
    main()
