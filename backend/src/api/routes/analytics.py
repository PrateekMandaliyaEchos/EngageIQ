"""Analytics endpoints for data insights and reporting."""

from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.core.config import get_settings

router = APIRouter()


@router.get("/segment-counts")
async def get_segment_counts():
    """
    Get the count of agents in each segment from Agent_persona.csv.
    
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
        # Get data path from settings
        settings = get_settings()
        data_location = settings._config.get('connectors', {}).get('csv', {}).get('location', './data')
        agent_file = Path(data_location) / "Agent_persona.csv"
        
        # Check if file exists
        if not agent_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Agent_persona.csv file not found at {agent_file}"
            )
        
        # Read CSV with proper error handling
        try:
            df = pd.read_csv(
                agent_file,
                low_memory=False,
                usecols=['Segment']  # Only read the Segment column for efficiency
            )
        except Exception as csv_error:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading CSV file: {str(csv_error)}"
            )
        
        # Check if Segment column exists
        if 'Segment' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Segment column not found in Agent_persona.csv"
            )
        
        # Count agents by segment
        segment_counts = df['Segment'].value_counts().to_dict()
        
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
    Get a comprehensive summary of the Agent_persona.csv dataset.
    
    Returns:
        JSON response with dataset statistics including:
        - Total agents
        - Segment distribution
        - Column information
        - File metadata
        
    Example Response:
    ```json
    {
        "total_agents": 3500,
        "total_columns": 45,
        "segment_counts": {
            "Independent Agents": 1500,
            "Comfortable retirees": 800
        },
        "file_info": {
            "file_size_mb": 12.5,
            "last_modified": "2025-01-01T12:00:00Z"
        }
    }
    ```
    """
    try:
        # Get data path from settings
        settings = get_settings()
        data_location = settings._config.get('connectors', {}).get('csv', {}).get('location', './data')
        agent_file = Path(data_location) / "Agent_persona.csv"
        
        # Check if file exists
        if not agent_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Agent_persona.csv file not found at {agent_file}"
            )
        
        # Read CSV with proper error handling
        try:
            df = pd.read_csv(agent_file, low_memory=False)
        except Exception as csv_error:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading CSV file: {str(csv_error)}"
            )
        
        # Get segment counts if Segment column exists
        segment_counts = {}
        if 'Segment' in df.columns:
            segment_counts = df['Segment'].value_counts().to_dict()
            segment_counts = {str(k): int(v) for k, v in segment_counts.items() if pd.notna(k)}
        
        # Get file metadata
        file_stat = agent_file.stat()
        file_size_mb = round(file_stat.st_size / (1024 * 1024), 2)
        
        return {
            "total_agents": len(df),
            "total_columns": len(df.columns),
            "segment_counts": segment_counts,
            "file_info": {
                "file_size_mb": file_size_mb,
                "last_modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).isoformat()
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
