# OpsPilot AI

**AI-Powered Operations & Customer Support Automation Platform**

OpsPilot AI is a full-stack operations automation project designed to demonstrate how AI can support customer service teams by analyzing support tickets, routing requests, managing approval workflows, and organizing operational data through a centralized dashboard.

The project combines backend development, AI-assisted decision-making, workflow automation, and business operations into one interactive application.

**[Live Demo](https://opspilot-ai-1v3q.onrender.com)** | **[GitHub Repository](https://github.com/JustinKvalo04/OpsPilot-AI)**

## Key Features

### AI-Assisted Ticket Analysis
- Analyzes incoming customer support requests.
- Supports ticket classification and prioritization.
- Routes tickets to appropriate departments.
- Supports configurable mock and LLM-assisted analysis modes.

### Workflow Automation
- Processes support tickets through structured workflows.
- Tracks ticket statuses and operational decisions.
- Supports automated ticket processing and routing.

### Human-in-the-Loop Approvals
- Allows human reviewers to approve or reject actions.
- Records reviewer information and decisions.
- Demonstrates how automated systems can maintain human oversight.

### Customer Response Management
- Supports creating and managing customer response drafts.
- Tracks response review and approval statuses.
- Maintains response-related audit records.

### Operations Dashboard
- Interactive dashboard built with Streamlit.
- Displays support tickets and operational information.
- Provides interfaces for reviewing tickets, managing workflows, and searching support policies.

### API Security and Monitoring
- API key authentication.
- Request rate limiting.
- Input validation.
- Audit logging and AI usage tracking.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend API | FastAPI |
| Dashboard | Streamlit |
| Database | SQLite |
| AI Integration | OpenAI API (optional) |
| Data Processing | Pandas |
| API Rate Limiting | SlowAPI |
| Cloud Hosting | Render |
| Version Control | Git & GitHub |

## System Architecture

The application uses a dashboard-to-API architecture:

```text
Streamlit Dashboard
        |
        v
    FastAPI Backend
        |
        +-- Ticket Analysis
        |
        +-- Workflow Automation
        |
        +-- Human Approval System
        |
        +-- Response Management
        |
        v
    SQLite Database
        |
        +-- Tickets
        +-- Audit Logs
        +-- AI Cache
        +-- AI Usage
        +-- Customer Responses
        +-- Response Audit
```

## Example Workflow

1. A support ticket is submitted through the dashboard.
2. The backend analyzes the ticket using the configured analysis mode.
3. The system assigns a priority and routes the ticket to an appropriate department.
4. The workflow determines the next processing step.
5. Actions requiring human oversight can be reviewed and approved or rejected.
6. Ticket activity and decisions are recorded for visibility and auditing.

## Run Locally

Clone the repository:

```bash
git clone https://github.com/JustinKvalo04/OpsPilot-AI.git
cd OpsPilot-AI
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables, including `OPSPILOT_API_KEY`, before starting the application.

For local demonstration without paid AI calls, use:

```text
AI_MODE=mock
ENABLE_PAID_AI=false
OPSPILOT_DEMO_MODE=true
```

Start the application:

```bash
./start.sh
```

Open the Streamlit dashboard at:

`http://localhost:8501`

## Public Demo

**[Try OpsPilot AI](https://opspilot-ai-1v3q.onrender.com)**

The hosted version runs in mock AI mode with fictional customer support scenarios.

Important limitations:

- The public demo uses a shared database.
- Visitors should only enter fictional information.
- No real customer records, passwords, or confidential data should be submitted.
- The hosted database uses temporary storage and may reset after redeployment or service restarts.
- The hosted demonstration does not make paid OpenAI API calls.

## Project Purpose

I built OpsPilot AI to gain hands-on experience developing AI-assisted business applications and operational workflows.

The project demonstrates how backend systems, automation, human oversight, and interactive dashboards can work together to support business processes.

It also reflects my interest in AI automation, AI operations, business systems, and practical applications of artificial intelligence.