# 🤖 EngageIQ: Intelligent Marketing Campaign Generator

**Engage the right agents, at the right time, with AI-driven personalized campaigns**

---

## 🏢 Industry Problem

In the U.S. insurance industry, distribution is driven by independent agents. There are approximately **1.2 million agents**, but engaging them effectively is a persistent challenge:

- Nearly **70% of agents leave** the business each year  
- Many **high-potential agents** (e.g., with strong Net Promoter Scores) are **underperforming in sales**  
- Marketing teams rely on **generic outreach** (e.g., wine tastings, mass emails), which fails to motivate agents meaningfully  

---

## 💡 Our Solution: EngageIQ

**EngageIQ** helps insurers and marketing teams **engage the right agents with the right campaign at the right time**.

---

## ⚙️ Key Capabilities

- **Targeting** – Identify agents with high potential but low sales performance.  
- **Personalization** – Match campaigns to an agent’s interests and persona  
  (e.g., fitness-oriented agents get gym offers, not wine tastings).  
- **Optimization** – Continuously refine engagement based on agent response and performance.  
- **Ease of Use** – Marketing teams can select segments and launch campaigns without heavy IT support.  

---

## 🧭 Example Marketing Workflow

1. **Segment Selection** – EngageIQ selects agents with high NPS but low policy sales.  
2. **360 Profile Enrichment** – Agent data (interests, behaviors, engagement history, surveys, complaints, sales, policy) is analyzed and target segment is shortlisted.  
3. **Campaign Recommendation** – EngageIQ suggests a personalized offer for target agents with a higher likelihood of selling.  
4. **Campaign Launch** – Marketing team approves and launches campaign.  
5. **Feedback Loop** – Engagement data feeds back to refine targeting.  


[Agent Data] → [Targeting Engine] → [Persona Insights] → [Campaign Match] → [Launch] → [Engagement Feedback]


---

## 🚀 Why It Matters

EngageIQ extends beyond insurance to any business that relies on **agents, representatives, or direct customer engagement**:

- Reduce attrition and strengthen loyalty among agents or reps.  
- Boost productivity and sales by identifying **high-potential, underperforming individuals**.  
- Increase ROI with **targeted, personalized campaigns**.  
- Scale to **customer engagement, cross-sell, and loyalty programs** across multiple segments.  
- Build stronger relationships with the **right offer, to the right person, at the right time**.  

---

## 📂 About This Repo

This repository contains a **prototype implementation** of EngageIQ, demonstrating how AI can be used to:

> Identify high-potential agents, personalize campaigns, and optimize engagement.

---

## 📘 What’s Included

- Example **agent datasets** with attributes like NPS, sales performance, and interests.  
- **Targeting engine workflows** to segment agents and predict engagement potential.  
- **Persona analysis modules** to match agents with personalized offers.  
- **Campaign simulation scripts** to test different outreach strategies.  
- **Feedback loop logic** to update agent profiles based on engagement outcomes.  

---

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
