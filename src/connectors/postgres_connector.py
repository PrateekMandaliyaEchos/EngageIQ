"""PostgreSQL connector for database operations."""

import pandas as pd
import json
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime


class PostgreSQLConnector:
    """
    PostgreSQL connector for database operations.
    
    Supports:
    - Database connection management
    - Table creation and management
    - Data insertion and retrieval
    - Pandas DataFrame integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PostgreSQL connector.
        
        Args:
            config: PostgreSQL configuration from config.yaml
        """
        self.config = config
        self.engine = None
        self.Session = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            # Build connection URL
            connection_url = self._build_connection_url()
            
            # Create engine
            self.engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ Connected to PostgreSQL database")
            
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {e}")
    
    def _build_connection_url(self) -> str:
        """Build PostgreSQL connection URL."""
        # Get credentials from environment variables
        user = os.getenv('POSTGRES_USER', self.config.get('user', 'postgres'))
        password = os.getenv('POSTGRES_PASSWORD', self.config.get('password', ''))
        host = os.getenv('POSTGRES_HOST', self.config.get('host', 'localhost'))
        port = os.getenv('POSTGRES_PORT', str(self.config.get('port', 5432)))
        database = os.getenv('POSTGRES_DB', self.config.get('database', 'engageiq'))
        
        # Handle Neon connection string format
        if 'DATABASE_URL' in os.environ:
            return os.environ['DATABASE_URL']
        
        # Build URL from components
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            with self.engine.connect() as conn:
                # Create agents table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agents (
                        agent_id VARCHAR(50) PRIMARY KEY,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        city VARCHAR(100),
                        education VARCHAR(50),
                        age INTEGER,
                        agent_tenure FLOAT,
                        aum_selfreported FLOAT,
                        nps_score FLOAT,
                        nps_feedback TEXT,
                        no_of_unique_policies_sold_last_12_months INTEGER,
                        premium_amount FLOAT,
                        segment VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create campaigns table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        campaign_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        goal TEXT NOT NULL,
                        target_criteria JSONB,
                        segment_size INTEGER,
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create campaign_results table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaign_results (
                        campaign_id VARCHAR(50) PRIMARY KEY,
                        campaign_name VARCHAR(200) NOT NULL,
                        llm_results JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create agent_profiles table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agent_profiles (
                        id SERIAL PRIMARY KEY,
                        campaign_id VARCHAR(50) NOT NULL,
                        agent_id VARCHAR(50) NOT NULL,
                        name VARCHAR(200),
                        segment VARCHAR(100),
                        aum FLOAT,
                        nps_score FLOAT,
                        tenure FLOAT,
                        policies_sold INTEGER,
                        age INTEGER,
                        city VARCHAR(100),
                        education VARCHAR(50),
                        premium_amount FLOAT,
                        nps_feedback TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
                    )
                """))
                
                conn.commit()
                print("✅ Database tables created successfully")
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to create tables: {e}")
    
    def insert_agents_from_csv(self, csv_file_path: str):
        """Insert agents from CSV file into database."""
        try:
            # Import CSV connector to read the file
            from .csv_connector import CSVConnector
            from src.core.config import get_settings
            
            # Get CSV connector configuration
            settings = get_settings()
            csv_config = settings.get_connector_config('csv')
            csv_connector = CSVConnector(csv_config)
            
            # Read CSV file using CSV connector
            df = csv_connector.read_csv(csv_file_path)
            
            # Clean and prepare data
            df = self._prepare_agent_data(df)
            
            # Insert into database
            df.to_sql('agents', self.engine, if_exists='replace', index=False, method='multi')
            
            print(f"✅ Inserted {len(df)} agents from {csv_file_path}")
            
        except Exception as e:
            raise Exception(f"Failed to insert agents: {e}")
    
    def _prepare_agent_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare agent data for database insertion."""
        # Map column names to database columns
        column_mapping = {
            'AGENT_ID': 'agent_id',
            'AGENT_FIRST_NAME': 'first_name',
            'AGENT_LAST_NAME': 'last_name',
            'CITY': 'city',
            'EDUCATION': 'education',
            'Age': 'age',
            'AGENT_TENURE': 'agent_tenure',
            'AUM_SELFREPORTED': 'aum_selfreported',
            'NPS_SCORE': 'nps_score',
            'NPS_FEEDBACK': 'nps_feedback',
            'NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS': 'no_of_unique_policies_sold_last_12_months',
            'PREMIUM_AMOUNT': 'premium_amount',
            'Segment': 'segment'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Select only the columns we need
        required_columns = list(column_mapping.values())
        df = df[[col for col in required_columns if col in df.columns]]
        
        # Clean data
        df = df.fillna('')
        df['agent_id'] = df['agent_id'].astype(str)
        
        return df
    
    def get_agents(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get agents from database with optional filters."""
        try:
            query = "SELECT * FROM agents"
            params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        conditions.append(f"{key} = %s")
                        params.append(value)
                    elif isinstance(value, dict):
                        if 'min' in value:
                            conditions.append(f"{key} >= %s")
                            params.append(value['min'])
                        if 'max' in value:
                            conditions.append(f"{key} <= %s")
                            params.append(value['max'])
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            return pd.read_sql(query, self.engine, params=params)
            
        except Exception as e:
            raise Exception(f"Failed to get agents: {e}")
    
    def insert_campaign(self, campaign_data: Dict[str, Any]) -> None:
        """Insert a new campaign into the database."""
        try:
            with self.Session() as session:
                # Convert target_criteria to JSON string if it's a dict
                if isinstance(campaign_data.get('target_criteria'), dict):
                    campaign_data['target_criteria'] = json.dumps(campaign_data['target_criteria'])
                
                # Insert campaign
                session.execute(text("""
                    INSERT INTO campaigns (campaign_id, name, goal, target_criteria, segment_size, status, created_at)
                    VALUES (:campaign_id, :name, :goal, :target_criteria, :segment_size, :status, :created_at)
                """), campaign_data)
                
                session.commit()
                print(f"✅ Campaign {campaign_data['campaign_id']} inserted successfully")
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to insert campaign: {e}")
    
    def update_campaign_llm_results(self, campaign_id: str, llm_results: Dict[str, Any]) -> None:
        """Update campaign with LLM-generated results."""
        try:
            with self.Session() as session:
                # Convert llm_results to JSON string
                llm_results_json = json.dumps(llm_results)
                
                # Update campaign with LLM results
                session.execute(text("""
                    UPDATE campaigns 
                    SET llm_results = :llm_results, 
                        status = 'completed',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE campaign_id = :campaign_id
                """), {
                    "campaign_id": campaign_id,
                    "llm_results": llm_results_json
                })
                
                session.commit()
                print(f"✅ Campaign {campaign_id} LLM results updated successfully")
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to update campaign LLM results: {e}")
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns from the database."""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    SELECT campaign_id, name, goal, target_criteria, segment_size, status, created_at, updated_at
                    FROM campaigns
                    ORDER BY created_at DESC
                """))
                
                campaigns = []
                for row in result:
                    campaign = dict(row._mapping)
                    # Parse JSON target_criteria if it's a string
                    if campaign.get('target_criteria') and isinstance(campaign['target_criteria'], str):
                        try:
                            campaign['target_criteria'] = json.loads(campaign['target_criteria'])
                        except (json.JSONDecodeError, TypeError):
                            # If it's not valid JSON, keep as is
                            pass
                    
                    campaigns.append(campaign)
                
                return campaigns
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to get campaigns: {e}")
    
    def insert_agent_profiles(self, campaign_id: str, agent_profiles: List[Dict[str, Any]]) -> None:
        """Insert agent profiles for a campaign."""
        try:
            with self.Session() as session:
                # Delete existing profiles for this campaign
                session.execute(text("DELETE FROM agent_profiles WHERE campaign_id = :campaign_id"), 
                              {"campaign_id": campaign_id})
                
                # Insert new profiles
                for profile in agent_profiles:
                    profile['campaign_id'] = campaign_id
                    session.execute(text("""
                        INSERT INTO agent_profiles (
                            campaign_id, agent_id, name, segment, aum, nps_score, tenure,
                            policies_sold, age, city, education, premium_amount, nps_feedback
                        ) VALUES (
                            :campaign_id, :agent_id, :name, :segment, :aum, :nps_score, :tenure,
                            :policies_sold, :age, :city, :education, :premium_amount, :nps_feedback
                        )
                    """), profile)
                
                session.commit()
                print(f"✅ Inserted {len(agent_profiles)} agent profiles for campaign {campaign_id}")
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to insert agent profiles: {e}")
    
    def get_agent_profiles(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get agent profiles for a campaign."""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    SELECT agent_id, name, segment, aum, nps_score, tenure, policies_sold,
                           age, city, education, premium_amount, nps_feedback
                    FROM agent_profiles
                    WHERE campaign_id = :campaign_id
                    ORDER BY name
                """), {"campaign_id": campaign_id})
                
                profiles = []
                for row in result:
                    profiles.append(dict(row._mapping))
                
                return profiles
                
        except SQLAlchemyError as e:
            raise Exception(f"Failed to get agent profiles: {e}")
    
    def insert_campaign_result(self, campaign_id: str, campaign_name: str, llm_results: Dict[str, Any]) -> None:
        """Insert or update campaign results in the campaign_results table."""
        try:
            with self.Session() as session:
                session.execute(text("""
                    INSERT INTO campaign_results (campaign_id, campaign_name, llm_results, updated_at)
                    VALUES (:campaign_id, :campaign_name, :llm_results, CURRENT_TIMESTAMP)
                    ON CONFLICT (campaign_id) 
                    DO UPDATE SET 
                        campaign_name = EXCLUDED.campaign_name,
                        llm_results = EXCLUDED.llm_results,
                        updated_at = CURRENT_TIMESTAMP
                """), {
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_name,
                    'llm_results': json.dumps(llm_results)
                })
                session.commit()
                print(f"✅ Campaign results for {campaign_id} saved successfully")
        except SQLAlchemyError as e:
            print(f"❌ Failed to save campaign results for {campaign_id}: {e}")
            raise
    
    def get_campaign_result(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign results from the campaign_results table."""
        try:
            with self.Session() as session:
                result = session.execute(text("""
                    SELECT campaign_id, campaign_name, llm_results, created_at, updated_at
                    FROM campaign_results
                    WHERE campaign_id = :campaign_id
                """), {"campaign_id": campaign_id})
                
                row = result.fetchone()
                if row:
                    campaign_result = dict(row._mapping)
                    # Parse JSON llm_results if it's a string
                    if campaign_result.get('llm_results') and isinstance(campaign_result['llm_results'], str):
                        try:
                            campaign_result['llm_results'] = json.loads(campaign_result['llm_results'])
                        except (json.JSONDecodeError, TypeError):
                            print(f"Warning: Could not decode llm_results for campaign {campaign_id}")
                            campaign_result['llm_results'] = {}
                    return campaign_result
                return None
                
        except SQLAlchemyError as e:
            print(f"❌ Failed to get campaign results for {campaign_id}: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            print("✅ Database connection closed")
