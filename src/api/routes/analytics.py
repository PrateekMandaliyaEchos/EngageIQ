"""Analytics endpoints for data insights and reporting."""

from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.core.config import get_settings
from src.connectors.factory import create_connector

router = APIRouter()


@router.get("/segment-counts")
async def get_segment_counts():
    """
    Get the count of agents in each segment from the database.
    
    Returns:
        JSON response with segment names as keys and counts as values,
        plus total agent count
        
    Example Response:
    ```json
    {
        "segment_counts": {
            "Independent Agents": 1500,
            "Comfortable retirees": 800,
            "Young professionals": 1200
        },
        "total_agents": 3500
    }
    ```
    """
    try:
        # Get settings and create connector
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Get agents from database
        agents = connector.get_agents()
        
        if agents is None or len(agents) == 0:
            raise HTTPException(
                status_code=404,
                detail="No agent data found in database"
            )
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(agents)
        
        # Check if segment column exists (handle both cases)
        segment_col = None
        for col in ['segment', 'Segment']:
            if col in df.columns:
                segment_col = col
                break
        
        if segment_col is None:
            raise HTTPException(
                status_code=400,
                detail="Segment column not found in agent data"
            )
        
        # Count agents by segment
        segment_counts = df[segment_col].value_counts().to_dict()
        
        # Convert any NaN values to 0 and ensure all values are integers
        segment_counts = {str(k): int(v) for k, v in segment_counts.items() if pd.notna(k)}
        
        # Calculate total agents
        total_agents = sum(segment_counts.values())
        
        return {
            "segment_counts": segment_counts,
            "total_agents": total_agents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving segment counts: {str(e)}"
        )


@router.get("/dataset-summary")
async def get_dataset_summary():
    """
    Get a comprehensive summary of the agent dataset from the database.
    
    Returns:
        JSON response with dataset statistics including:
        - Total agents
        - Segment distribution
        - Column information
        - Database metadata
        
    Example Response:
    ```json
    {
        "total_agents": 3500,
        "total_columns": 45,
        "segment_counts": {
            "Independent Agents": 1500,
            "Comfortable retirees": 800
        },
        "database_info": {
            "connector_type": "postgresql",
            "data_source": "database"
        }
    }
    ```
    """
    try:
        # Get settings and create connector
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Get agents from database
        agents = connector.get_agents()
        
        if agents is None or len(agents) == 0:
            raise HTTPException(
                status_code=404,
                detail="No agent data found in database"
            )
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(agents)
        
        # Get segment counts if segment column exists (handle both cases)
        segment_counts = {}
        segment_col = None
        for col in ['segment', 'Segment']:
            if col in df.columns:
                segment_col = col
                break
        
        if segment_col:
            segment_counts = df[segment_col].value_counts().to_dict()
            segment_counts = {str(k): int(v) for k, v in segment_counts.items() if pd.notna(k)}
        
        return {
            "total_agents": len(df),
            "total_columns": len(df.columns),
            "segment_counts": segment_counts,
            "database_info": {
                "connector_type": connector_type,
                "data_source": "database"
            },
            "columns": list(df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dataset summary: {str(e)}"
        )
