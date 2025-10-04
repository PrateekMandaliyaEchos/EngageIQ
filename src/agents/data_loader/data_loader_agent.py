"""Data Loader Agent - Loads insurance agent population data from CSV files."""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path

from src.agents.base_agent import BaseAgent, Message
from src.core.config import get_settings


class DataLoaderAgent(BaseAgent):
    """
    Data Loader Agent that loads unified insurance agent population data.
    
    Responsibilities:
    1. Load the unified Agent_persona.csv file (contains all agent data)
    2. Return structured DataFrame with complete agent records
    3. Handle data validation and error cases
    
    Note: All previously separate data sources (complaints, discovery, infutor, 
    policy data, survey data) are now unified in the single Agent_persona.csv file.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data loader agent.
        
        Args:
            config: Agent configuration from config.yaml
        """
        settings = get_settings()
        agent_config = settings.get_agent_config('data_loader')
        super().__init__("DataLoader", agent_config)
        
        self.settings = settings
        self.data_cache = {}  # Cache loaded data
        
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Load agent data from the unified Agent_persona.csv file.
        
        Args:
            message: Message containing data source preferences (include_additional is ignored)
            
        Returns:
            Dictionary with loaded data and metadata
        """
        try:
            # Load unified agent persona data (now contains all previously separate data)
            agent_data = self._load_agent_persona_data()
            
            # Clean sample data for JSON serialization
            sample_data = []
            if isinstance(agent_data, pd.DataFrame):
                sample_df = agent_data.head(3).fillna("N/A")  # Replace NaN with "N/A"
                sample_data = sample_df.to_dict('records')
            
            return {
                "success": True,
                "agent_data": "Unified dataset loaded successfully",
                "metadata": {
                    "total_agents": len(agent_data),
                    "data_sources_loaded": ['agent_persona_unified'],
                    "columns": list(agent_data.columns) if isinstance(agent_data, pd.DataFrame) else [],
                    "sample_data": sample_data,
                    "note": "All data (complaints, discovery, infutor, policy, survey) now unified in Agent_persona.csv"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Data loading failed: {str(e)}",
                "agent_data": None
            }
    
    def _load_agent_persona_data(self) -> pd.DataFrame:
        """
        Load the unified agent persona CSV file containing all agent data.
        
        This file now includes all previously separate data sources:
        - Agent persona information
        - Complaints data
        - Discovery data
        - Infutor data
        - Policy data
        - Survey data
        
        Returns:
            DataFrame with complete unified agent data
        """
        # Get data path from config
        data_sources = self.settings.data_sources
        csv_config = self.settings.get_connector_config('csv')
        data_path = Path(csv_config.get('location', './data'))
        
        # Handle the actual filename with spaces
        agent_file = data_path / "Agent_persona.csv"
        
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent persona file not found: {agent_file}")
        
        # Load CSV with proper handling
        df = pd.read_csv(
            agent_file,
            delimiter=csv_config.get('delimiter', ','),
            encoding=csv_config.get('encoding', 'utf-8'),
            skiprows=csv_config.get('skip_rows', 0),
            low_memory=False
        )
        
        # Cache the data
        self.data_cache['agent_persona'] = df
        
        return df
    
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of loaded data.
        
        Returns:
            Dictionary with data summary
        """
        if 'agent_persona' not in self.data_cache:
            return {"error": "No data loaded yet"}
        
        df = self.data_cache['agent_persona']
        
        # Key metrics for campaign criteria
        summary = {
            "total_agents": len(df),
            "segments": df['Segment'].value_counts().to_dict() if 'Segment' in df.columns else {},
            "aum_stats": {
                "mean": df['AUM_SELFREPORTED'].mean() if 'AUM_SELFREPORTED' in df.columns else None,
                "median": df['AUM_SELFREPORTED'].median() if 'AUM_SELFREPORTED' in df.columns else None,
                "q75": df['AUM_SELFREPORTED'].quantile(0.75) if 'AUM_SELFREPORTED' in df.columns else None,
                "q90": df['AUM_SELFREPORTED'].quantile(0.90) if 'AUM_SELFREPORTED' in df.columns else None
            },
            "nps_stats": {
                "mean": df['NPS_SCORE'].mean() if 'NPS_SCORE' in df.columns else None,
                "median": df['NPS_SCORE'].median() if 'NPS_SCORE' in df.columns else None,
                "q75": df['NPS_SCORE'].quantile(0.75) if 'NPS_SCORE' in df.columns else None
            },
            "tenure_stats": {
                "mean": df['AGENT_TENURE'].mean() if 'AGENT_TENURE' in df.columns else None,
                "median": df['AGENT_TENURE'].median() if 'AGENT_TENURE' in df.columns else None
            }
        }
        
        return summary
