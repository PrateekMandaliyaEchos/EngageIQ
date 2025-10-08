#!/usr/bin/env python3
"""
Database migration script to create campaign_results table.
"""

import os
import sys
sys.path.append('/app')

from src.core.config import get_settings
from src.connectors.factory import create_connector
from sqlalchemy import text, inspect

def create_campaign_results_table():
    """Create campaign_results table."""
    try:
        print("🔄 Creating campaign_results table...")
        
        # Get settings and create connector
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Create campaign_results table
        with connector.engine.connect() as conn:
            inspector = inspect(conn)
            
            # Check if table already exists
            if 'campaign_results' in inspector.get_table_names():
                print("✅ campaign_results table already exists")
                return
            
            # Create the table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS campaign_results (
                    campaign_id VARCHAR(50) PRIMARY KEY,
                    campaign_name VARCHAR(200) NOT NULL,
                    llm_results JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("✅ Created campaign_results table successfully")
        
        print("✅ Database migration completed.")
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_campaign_results_table()
