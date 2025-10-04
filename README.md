# 🤖 EngageIQ: Intelligent Marketing Campaign Generator

EngageIQ is an AI-powered multi-agent system designed to automate and optimize marketing campaign generation for insurance agents. The system uses natural language processing and structured data analysis to create targeted, data-driven marketing campaigns.

## 🎯 Project Overview

EngageIQ allows users to submit natural language campaign goals (e.g., "Create a campaign targeting high-NPS agents with declining sales") and automatically generates comprehensive campaign strategies using:

- LLM-powered analysis (Claude via LangChain)
- Multi-agent orchestration
- Data-driven segmentation
- Automated strategy generation

### 🧠 Core Features

- Natural language campaign goal interpretation
- Intelligent data segmentation and analysis
- Automated campaign strategy generation
- REST API interface
- Persistent campaign storage
- Multi-agent architecture for complex reasoning

## 🏗 System Architecture

### Component Overview

1. **Config Layer**

   - YAML-based configuration
   - Environment-specific settings
   - Data source configuration

2. **LLM Layer**

   - Claude integration via LangChain
   - Abstract provider interface
   - Structured output parsing

3. **Agent Layer**

   - Goal Parser Agent: Interprets campaign objectives
   - Data Loader Agent: Manages data access
   - Segmentation Agent: Filters target populations
   - Profile Generator Agent: Creates segment analytics
   - Campaign Strategist Agent: Generates tactics
   - Orchestrator Agent: Coordinates workflow

4. **Service Layer**

   - Campaign management
   - Request handling
   - Data persistence

5. **API Layer**
   - FastAPI-based REST interface
   - Campaign creation endpoints
   - Campaign retrieval endpoints

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/PrateekMandaliyaEchos/EngageIQ.git
   cd EngageIQ
   \`\`\`

2. Create and activate virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\\Scripts\\activate
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

### Configuration

1. Copy the example configuration:
   \`\`\`bash
   cp config.yaml.example config.yaml
   \`\`\`

2. Update configuration in \`config.yaml\`:
   \`\`\`yaml
   app:
   name: EngageIQ
   version: 1.0.0
   environment: development # development, staging, production
   debug: true

api:
host: 0.0.0.0
port: 8000
cors_origins: - http://localhost:3000

# Add your specific configurations

\`\`\`

### Running the Application

1. Start the API server:
   \`\`\`bash
   python src/api/run_server.py
   \`\`\`

2. The API will be available at \`http://localhost:8000\`

## 📚 API Documentation

### Create Campaign

\`\`\`http
POST /api/v1/campaigns/create
Content-Type: application/json

{
"goal": "Find high-value agents with excellent satisfaction for VIP retention"
}
\`\`\`

### List All Campaigns

\`\`\`http
GET /api/v1/campaigns/all
\`\`\`

## 📁 Project Structure

\`\`\`
├── config.yaml # Application configuration
├── requirements.txt # Python dependencies
├── data/ # Data directory
│ ├── Agent Persona.csv
│ ├── Complaints.csv
│ ├── Discovery.csv
│ ├── campaigns.csv
│ └── ...
└── src/
├── agents/ # Multi-agent system
│ ├── base_agent.py
│ ├── orchestrator/
│ ├── goal_parser/
│ └── ...
├── api/ # FastAPI application
│ ├── app.py
│ └── routes/
├── core/ # Core utilities
│ └── config/
├── llm/ # LLM integration
│ ├── base_provider.py
│ └── claude.py
└── services/ # Business logic
└── campaign_service.py
\`\`\`

## 🔧 Development

### Adding New Agents

1. Create a new directory under \`src/agents/\`
2. Implement the agent class extending \`BaseAgent\`
3. Register the agent with the orchestrator

Example:
\`\`\`python
from src.agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
def process(self, message): # Implement agent logic
pass
\`\`\`

### Data Sources

The system supports multiple data sources:

- Local CSV files (default)
- S3 storage (configurable)
- Database connections (extensible)

Configure data sources in \`config.yaml\` under the \`data.connectors\` section.

## 📝 Testing

Run tests using pytest:
\`\`\`bash
pytest
\`\`\`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI and LangChain
- Powered by Anthropic's Claude
- Inspired by multi-agent AI architectures
