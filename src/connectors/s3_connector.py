"""S3 connector for reading and writing data files."""

import boto3
import pandas as pd
import json
import io
from typing import Dict, Any, Optional, List
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError


class S3Connector:
    """
    S3 connector for reading and writing data files.
    
    Supports:
    - CSV file operations
    - JSON file operations
    - Directory listing
    - File existence checks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize S3 connector.
        
        Args:
            config: S3 configuration from config.yaml
        """
        self.config = config
        self.bucket = config.get('bucket')
        self.region = config.get('region', 'us-east-1')
        self.prefix = config.get('prefix', '')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=config.get('credentials', {}).get('access_key_id'),
                aws_secret_access_key=config.get('credentials', {}).get('secret_access_key')
            )
        except NoCredentialsError:
            raise ValueError("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    
    def _get_s3_key(self, filename: str) -> str:
        """Get full S3 key for a filename."""
        if self.prefix:
            return f"{self.prefix.rstrip('/')}/{filename}"
        return filename
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            s3_key = self._get_s3_key(filename)
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def read_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Read CSV file from S3.
        
        Args:
            filename: Name of the CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with the CSV data
        """
        try:
            s3_key = self._get_s3_key(filename)
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            
            # Read CSV from S3 response
            csv_content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content), **kwargs)
            
            return df
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {filename}")
            raise
    
    def write_csv(self, df: pd.DataFrame, filename: str, **kwargs) -> None:
        """
        Write DataFrame to CSV in S3.
        
        Args:
            df: DataFrame to write
            filename: Name of the CSV file
            **kwargs: Additional arguments for df.to_csv
        """
        try:
            s3_key = self._get_s3_key(filename)
            
            # Convert DataFrame to CSV string
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, **kwargs)
            csv_content = csv_buffer.getvalue()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=csv_content.encode('utf-8'),
                ContentType='text/csv'
            )
        except ClientError as e:
            raise Exception(f"Failed to write CSV to S3: {e}")
    
    def read_json(self, filename: str) -> Dict[str, Any]:
        """
        Read JSON file from S3.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Dictionary with the JSON data
        """
        try:
            s3_key = self._get_s3_key(filename)
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            
            # Read JSON from S3 response
            json_content = response['Body'].read().decode('utf-8')
            return json.loads(json_content)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {filename}")
            raise
    
    def write_json(self, data: Dict[str, Any], filename: str, **kwargs) -> None:
        """
        Write data to JSON file in S3.
        
        Args:
            data: Data to write
            filename: Name of the JSON file
            **kwargs: Additional arguments for json.dump
        """
        try:
            s3_key = self._get_s3_key(filename)
            
            # Convert data to JSON string
            json_content = json.dumps(data, **kwargs)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=json_content.encode('utf-8'),
                ContentType='application/json'
            )
        except ClientError as e:
            raise Exception(f"Failed to write JSON to S3: {e}")
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in S3 bucket with optional prefix.
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file names
        """
        try:
            full_prefix = self._get_s3_key(prefix) if prefix else self.prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=full_prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Remove prefix from key to get just filename
                    key = obj['Key']
                    if self.prefix and key.startswith(self.prefix):
                        files.append(key[len(self.prefix):].lstrip('/'))
                    else:
                        files.append(key)
            
            return files
        except ClientError as e:
            raise Exception(f"Failed to list files in S3: {e}")
    
    def delete_file(self, filename: str) -> None:
        """
        Delete file from S3.
        
        Args:
            filename: Name of the file to delete
        """
        try:
            s3_key = self._get_s3_key(filename)
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {e}")
    
    def create_directory(self, dirname: str) -> None:
        """
        Create a directory in S3 (by creating an empty object with trailing slash).
        
        Args:
            dirname: Name of the directory to create
        """
        try:
            s3_key = self._get_s3_key(f"{dirname}/")
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=b'',
                ContentType='application/x-directory'
            )
        except ClientError as e:
            raise Exception(f"Failed to create directory in S3: {e}")
