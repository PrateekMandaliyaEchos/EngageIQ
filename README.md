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

## TEMP
## Comprehensive Campaign Strategy: High-Performer Recognition & Retention\n\n**Strategic Overview and Objectives**\n\nThis retention-focused campaign targets a highly select group of 5 exceptional agents who have demonstrated superior performance within their first 12 months, positioning them as critical assets requiring immediate investment to prevent competitive poaching. The primary objective centers on reinforcing their value to the organization while addressing the identified \"moderate satisfaction\" gap that represents a significant retention risk. Over the 4-6 week timeline, we will implement a multi-touch recognition strategy that combines exclusive benefits with personalized career development opportunities, ultimately driving satisfaction scores above the 85th percentile while securing 12-month retention commitments. The campaign will establish these agents as brand ambassadors and potential mentors for future new agent cohorts, creating a sustainable competitive advantage in agent acquisition and development.\n\n**Target Audience Analysis and Approach**\n\nOur target segment represents a unique paradox: high-performing agents with moderate satisfaction levels, indicating untapped potential for deeper engagement and loyalty. These agents possess proven premium generation capabilities that exceed their peer cohort benchmarks, yet their satisfaction scores suggest they may be susceptible to competitor recruitment efforts or internal disengagement. The approach will leverage their achievement-oriented mindset by providing exclusive access to senior leadership, advanced training opportunities, and preferential territory assignments that align with their proven success patterns. Given their recent entry into the organization, they require validation of their career choice while receiving clear pathways for advancement that match their accelerated performance trajectory. The messaging will emphasize their exceptional status within the new agent population while providing tangible benefits that reinforce their decision to join and excel within our organization.\n\n**Implementation Framework and Tactics**\n\nThe campaign will deploy a three-phase email sequence complemented by high-touch personal interactions to maximize impact and engagement. Phase 1 (Week 1-2) launches with a personalized recognition email from senior leadership, highlighting specific performance metrics and announcing their selection for an exclusive \"Rising Stars\" program, followed by a premium gift package delivery. Phase 2 (Week 2-4) focuses on exclusive benefits activation, including priority access to high-value leads, advanced product training webinars, and invitation to a quarterly leadership roundtable with C-suite executives. Phase 3 (Week 4-6) emphasizes future opportunity through personalized career development consultations, mentor program enrollment, and early access to new product launches or territory expansions. Each email will include satisfaction pulse surveys and engagement tracking, while personal touches such as handwritten notes from regional managers and exclusive company merchandise will reinforce the premium experience throughout the campaign timeline.\n\n**Expected Outcomes and Success Factors**\n\nSuccess metrics will focus on both immediate engagement and long-term retention indicators, with target benchmarks including 90%+ email open rates, 75%+ click-through rates on exclusive content, and measurable satisfaction score improvements of at least 20 percentage points within the campaign period. The campaign should generate 100% participation in offered exclusive programs, with at least 80% of agents expressing increased loyalty and career commitment through follow-up surveys. Long-term success factors include 12-month retention rates exceeding 95% for this cohort, continued premium production growth of 15%+ quarter-over-quarter, and successful transition of at least 60% of participants into mentor roles for subsequent new agent classes. The campaign's effectiveness will ultimately be measured by its ability to transform moderate satisfaction into advocacy, creating a replicable model for future high-performer retention while establishing these agents as internal champions who actively contribute to recruitment and culture-building initiatives that strengthen overall agent satisfaction and organizational performance.
