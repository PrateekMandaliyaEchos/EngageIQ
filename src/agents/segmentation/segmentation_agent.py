"""Segmentation Agent - Filters agent population based on parsed criteria."""

import pandas as pd
from typing import Dict, Any, List, Union

from src.agents.base_agent import BaseAgent, Message
from src.core.config import get_settings


class SegmentationAgent(BaseAgent):
    """
    Segmentation Agent that filters agent population based on parsed criteria.
    
    Responsibilities:
    1. Take criteria from GoalParser + data from DataLoader
    2. Apply constraints (AUM > X, NPS >= Y, etc.)
    3. Return matching agent IDs/records
    4. Provide segmentation statistics
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize segmentation agent.
        
        Args:
            config: Agent configuration from config.yaml
        """
        settings = get_settings()
        agent_config = settings.get_agent_config('segmentation')
        super().__init__("SegmentationAgent", agent_config)
        
        self.settings = settings
        
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Filter agent population based on criteria.
        
        Args:
            message: Message containing criteria and agent data
            
        Returns:
            Dictionary with filtered agents and statistics
        """
        try:
            # Extract criteria and agent data from message
            criteria = message.content.get('criteria', {})
            agent_data = message.content.get('agent_data', {})
            
            if not criteria:
                raise ValueError("No criteria provided for segmentation")
            
            if not agent_data or not agent_data.get('success'):
                raise ValueError("No valid agent data provided for segmentation")
            
            # Get the actual DataFrame from DataLoader cache
            from src.agents.data_loader import DataLoaderAgent
            data_loader = DataLoaderAgent({})
            data_result = data_loader.process(
                Message(
                    sender=self.name,
                    recipient="DataLoader",
                    content={},  # Load unified dataset
                    message_type="load_data"
                )
            )
            
            if not data_result.get('success'):
                raise ValueError(f"Failed to load agent data: {data_result.get('error')}")
            
            # Get the full dataset from the DataLoader's cache
            if hasattr(data_loader, 'data_cache') and 'agent_persona' in data_loader.data_cache:
                agent_df = data_loader.data_cache['agent_persona']
            else:
                # Fallback to sample data if full dataset not available in cache
                agent_df = self._convert_to_dataframe(data_result['metadata']['sample_data'])
            
            # Apply segmentation criteria
            filtered_agents = self._apply_criteria(agent_df, criteria)
            
            # Generate segmentation statistics
            stats = self._generate_segmentation_stats(agent_df, filtered_agents, criteria)
            
            # Convert numpy types to native Python types for JSON serialization
            agent_ids = []
            if 'AGENT_ID' in filtered_agents.columns:
                agent_ids = [int(x) if pd.notna(x) else None for x in filtered_agents['AGENT_ID'].tolist()]
            
            sample_filtered = []
            if len(filtered_agents) > 0:
                sample_df = filtered_agents.head(5).fillna("N/A")
                sample_filtered = sample_df.to_dict('records')
            
            return {
                "success": True,
                "total_agents": int(len(agent_df)),  # This will now be the full dataset size
                "filtered_agents": int(len(filtered_agents)),
                "agent_ids": agent_ids,
                "criteria_applied": criteria,
                "statistics": stats,
                "sample_filtered": sample_filtered
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Segmentation failed: {str(e)}",
                "total_agents": 0,
                "filtered_agents": 0,
                "agent_ids": []
            }
    
    def _convert_to_dataframe(self, sample_data: List[Dict]) -> pd.DataFrame:
        """
        Convert sample data back to DataFrame for filtering.
        Note: This is a simplified approach. In production, you'd want to 
        maintain the full DataFrame in memory or use a proper data store.
        """
        # For demonstration, we'll create a mock DataFrame with the expected structure
        # In a real implementation, you'd load the full dataset
        if not sample_data:
            return pd.DataFrame()
        
        # Create a DataFrame from sample data
        df = pd.DataFrame(sample_data)
        
        # Convert numeric columns properly
        numeric_columns = ['AUM_SELFREPORTED', 'NPS_SCORE', 'AGENT_TENURE', 'NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS', 'COMPLAINTS_LAST_12_MONTHS']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _apply_criteria(self, df: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filtering criteria to agent DataFrame.
        
        Args:
            df: Agent DataFrame
            criteria: Parsed criteria from GoalParser
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        filtered_df = df.copy()
        constraints = criteria.get('constraints', [])
        
        for constraint in constraints:
            field = constraint.get('field')
            operator = constraint.get('operator')
            value = constraint.get('value')
            
            if not all([field, operator, value is not None]):
                continue
            
            # Apply the constraint
            if field in filtered_df.columns:
                if operator == '>':
                    filtered_df = filtered_df[filtered_df[field] > value]
                elif operator == '>=':
                    filtered_df = filtered_df[filtered_df[field] >= value]
                elif operator == '<':
                    filtered_df = filtered_df[filtered_df[field] < value]
                elif operator == '<=':
                    filtered_df = filtered_df[filtered_df[field] <= value]
                elif operator == '==':
                    filtered_df = filtered_df[filtered_df[field] == value]
                elif operator == '!=':
                    filtered_df = filtered_df[filtered_df[field] != value]
        
        return filtered_df
    
    def _generate_segmentation_stats(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate segmentation statistics.
        
        Args:
            original_df: Original agent DataFrame
            filtered_df: Filtered agent DataFrame
            criteria: Applied criteria
            
        Returns:
            Statistics dictionary
        """
        stats = {
            "segmentation_rate": float(len(filtered_df) / len(original_df)) if len(original_df) > 0 else 0.0,
            "criteria_count": int(len(criteria.get('constraints', []))),
            "objective": criteria.get('objective', 'unknown')
        }
        
        # Add field-specific statistics
        key_fields = ['AUM_SELFREPORTED', 'NPS_SCORE', 'AGENT_TENURE']
        
        for field in key_fields:
            if field in original_df.columns and field in filtered_df.columns:
                stats[f"{field}_original"] = {
                    "mean": float(original_df[field].mean()) if pd.notna(original_df[field].mean()) else None,
                    "median": float(original_df[field].median()) if pd.notna(original_df[field].median()) else None,
                    "min": float(original_df[field].min()) if pd.notna(original_df[field].min()) else None,
                    "max": float(original_df[field].max()) if pd.notna(original_df[field].max()) else None
                }
                
                if len(filtered_df) > 0:
                    stats[f"{field}_filtered"] = {
                        "mean": float(filtered_df[field].mean()) if pd.notna(filtered_df[field].mean()) else None,
                        "median": float(filtered_df[field].median()) if pd.notna(filtered_df[field].median()) else None,
                        "min": float(filtered_df[field].min()) if pd.notna(filtered_df[field].min()) else None,
                        "max": float(filtered_df[field].max()) if pd.notna(filtered_df[field].max()) else None
                    }
        
        return stats
