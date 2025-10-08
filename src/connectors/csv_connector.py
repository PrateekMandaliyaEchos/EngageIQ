"""CSV connector for local file operations."""

import pandas as pd
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class CSVConnector:
    """
    CSV connector for local file operations.
    
    Supports:
    - CSV file operations
    - JSON file operations
    - Directory operations
    - File existence checks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CSV connector.
        
        Args:
            config: CSV configuration from config.yaml
        """
        self.config = config
        self.base_path = Path(config.get('location', './data'))
        self.base_path.mkdir(exist_ok=True)
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full file path for a filename."""
        return self.base_path / filename
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists locally.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        return self._get_file_path(filename).exists()
    
    def read_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Read CSV file from local filesystem.
        
        Args:
            filename: Name of the CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with the CSV data
        """
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Set default parameters from config
        default_params = {
            'delimiter': self.config.get('delimiter', ','),
            'encoding': self.config.get('encoding', 'utf-8'),
            'skiprows': self.config.get('skip_rows', 0),
            'low_memory': False
        }
        
        # Merge with provided kwargs
        read_params = {**default_params, **kwargs}
        
        return pd.read_csv(file_path, **read_params)
    
    def write_csv(self, df: pd.DataFrame, filename: str, **kwargs) -> None:
        """
        Write DataFrame to CSV file locally.
        
        Args:
            df: DataFrame to write
            filename: Name of the CSV file
            **kwargs: Additional arguments for df.to_csv
        """
        file_path = self._get_file_path(filename)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV
        df.to_csv(file_path, **kwargs)
    
    def read_json(self, filename: str) -> Dict[str, Any]:
        """
        Read JSON file from local filesystem.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Dictionary with the JSON data
        """
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_json(self, data: Dict[str, Any], filename: str, **kwargs) -> None:
        """
        Write data to JSON file locally.
        
        Args:
            data: Data to write
            filename: Name of the JSON file
            **kwargs: Additional arguments for json.dump
        """
        file_path = self._get_file_path(filename)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, **kwargs)
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in local directory with optional prefix.
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file names
        """
        if prefix:
            pattern = f"{prefix}*"
        else:
            pattern = "*"
        
        files = []
        for file_path in self.base_path.glob(pattern):
            if file_path.is_file():
                files.append(file_path.name)
        
        return files
    
    def delete_file(self, filename: str) -> None:
        """
        Delete file from local filesystem.
        
        Args:
            filename: Name of the file to delete
        """
        file_path = self._get_file_path(filename)
        if file_path.exists():
            file_path.unlink()
    
    def create_directory(self, dirname: str) -> None:
        """
        Create a directory locally.
        
        Args:
            dirname: Name of the directory to create
        """
        dir_path = self.base_path / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
