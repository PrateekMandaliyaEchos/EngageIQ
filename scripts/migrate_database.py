#!/usr/bin/env python3
"""
Database migration script to add llm_results column to campaigns table.
"""

import os
import sys
sys.path.append('/app')

from src.core.config import get_settings
from src.connectors.factory import create_connector

def migrate_database():
    """Add llm_results column to campaigns table."""
    try:
        print("🔄 Starting database migration...")
        
        # Get settings and create connector
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Add llm_results column to campaigns table
        with connector.engine.connect() as conn:
            from sqlalchemy import text
            
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' AND column_name = 'llm_results'
            """))
            
            if result.fetchone():
                print("✅ llm_results column already exists")
            else:
                # Add the column
                conn.execute(text("""
                    ALTER TABLE campaigns 
                    ADD COLUMN llm_results JSONB
                """))
                conn.commit()
                print("✅ Added llm_results column to campaigns table")
        
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_database()
