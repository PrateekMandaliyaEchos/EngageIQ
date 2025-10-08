"""Factory for creating data connectors."""

from typing import Dict, Any
from .csv_connector import CSVConnector
from .s3_connector import S3Connector
from .postgres_connector import PostgreSQLConnector


def create_connector(connector_type: str, config: Dict[str, Any]):
    """
    Create a data connector based on type.
    
    Args:
        connector_type: Type of connector ('csv', 's3', 'postgres', etc.)
        config: Configuration for the connector
        
    Returns:
        Connector instance
        
    Raises:
        ValueError: If connector type is not supported
    """
    if connector_type == 'csv':
        return CSVConnector(config)
    elif connector_type == 's3':
        return S3Connector(config)
    elif connector_type == 'postgres':
        return PostgreSQLConnector(config)
    else:
        raise ValueError(f"Unsupported connector type: {connector_type}")
