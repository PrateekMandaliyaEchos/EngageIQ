#!/usr/bin/env python3
"""
Script to initialize data in the database.
This ensures agent data is always available when the container starts.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from connectors.factory import create_connector
from core.config import get_settings


def init_agent_data():
    """Initialize agent data in the database."""
    try:
        # Get settings
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        
        # Create connector
        connector = create_connector(connector_type, connector_config)
        
        print("🔧 Setting up database tables...")
        connector.create_tables()
        
        # Check if agents table has data
        try:
            agents = connector.get_agents()
            if len(agents) > 0:
                print(f"✅ Agent data already exists ({len(agents)} agents)")
                return
        except Exception as e:
            print(f"⚠️  Could not check existing agents: {e}")
        
        # Load agent data from CSV if available
        csv_connector = create_connector('csv', settings.get_connector_config('csv'))
        agent_file = "Agent_persona.csv"
        
        print(f"🔍 Looking for agent file at: {agent_file}")
        print(f"🔍 CSV connector base path: {csv_connector.base_path}")
        print(f"🔍 Full path: {csv_connector.base_path / agent_file}")
        
        if csv_connector.file_exists(agent_file):
            print("📊 Loading agent data from CSV to database...")
            connector.insert_agents_from_csv(agent_file)
            print("✅ Agent data loaded successfully")
        else:
            print("⚠️  No agent CSV file found. Please ensure data/Agent_persona.csv exists.")
            print(f"   Expected file: {csv_connector.base_path / agent_file}")
            print(f"   Files in data directory: {list(csv_connector.base_path.glob('*'))}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        return False


if __name__ == "__main__":
    success = init_agent_data()
    if not success:
        sys.exit(1)
    print("🎉 Data initialization complete!")
