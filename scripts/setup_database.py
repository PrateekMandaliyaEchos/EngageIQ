#!/usr/bin/env python3
"""
Script to set up the database and migrate data from CSV to PostgreSQL.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from connectors.factory import create_connector
from core.config import get_settings


def setup_database():
    """Set up database tables and migrate data."""
    try:
        # Get settings
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        
        # Create connector
        connector = create_connector(connector_type, connector_config)
        
        print("🔧 Setting up database tables...")
        connector.create_tables()
        
        # Check if we have CSV data to migrate
        csv_connector = create_connector('csv', settings.get_connector_config('csv'))
        agent_file = "Agent_persona.csv"
        
        print(f"🔍 Looking for agent file at: {agent_file}")
        print(f"🔍 CSV connector base path: {csv_connector.base_path}")
        
        if csv_connector.file_exists(agent_file):
            print("📊 Migrating agent data from CSV to database...")
            connector.insert_agents_from_csv(agent_file)
            print("✅ Agent data migration complete!")
        else:
            print("⚠️  No agent CSV file found. Skipping data migration.")
            print(f"   Expected file: {csv_connector.base_path / agent_file}")
            print(f"   Files in data directory: {list(csv_connector.base_path.glob('*'))}")
        
        print("✅ Database setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def migrate_csv_to_postgres():
    """Migrate existing CSV data to PostgreSQL."""
    try:
        # Get settings
        settings = get_settings()
        
        # Create PostgreSQL connector
        postgres_connector = create_connector('postgres', settings.get_connector_config('postgres'))
        
        # Create CSV connector
        csv_connector = create_connector('csv', settings.get_connector_config('csv'))
        
        print("🔄 Migrating campaigns from CSV to PostgreSQL...")
        
        # Migrate campaigns
        campaigns_file = "campaigns.csv"
        if csv_connector.file_exists(campaigns_file):
            df = csv_connector.read_csv(campaigns_file)
            
            for _, campaign in df.iterrows():
                campaign_data = {
                    'campaign_id': campaign['campaign_id'],
                    'name': campaign['name'],
                    'goal': campaign['goal'],
                    'target_criteria': campaign['target_criteria'],
                    'segment_size': campaign['segment_size'],
                    'status': campaign['status'],
                    'created_at': campaign['created_at']
                }
                postgres_connector.insert_campaign(campaign_data)
            
            print(f"✅ Migrated {len(df)} campaigns")
        else:
            print("⚠️  No campaigns CSV file found")
        
        print("✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        migrate_csv_to_postgres()
    else:
        setup_database()
