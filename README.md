# Red Team Actor Simulator

A framework for testing AI model safety and robustness through simulated adversarial scenarios. An "Actor Agent" role-plays configurable personas to probe a "Subject Model" toward defined objectives, while an "Assessor Agent" evaluates progress against completion criteria.

## Features

- **Configurable Personas**: Test with different skill levels (novice/semi-skilled/expert), resource availability (low/medium/high), and backgrounds (technical/non-technical)
- **Multi-Provider Support**: OpenAI, Anthropic, Google AI, and Ollama (local models)
- **Objective Chaining**: Simulate multi-step "harm journeys" to identify bottlenecks
- **Sneaky Mode**: Give the actor visibility into completion criteria, subject's chain-of-thought, and assessor hints
- **Session Persistence**: SQLite database with JSON import/export
- **Comprehensive Reports**: Markdown and PDF output with strategy analysis

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys for at least one provider (OpenAI, Anthropic, or Google)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Configuration

Edit `backend/.env` to configure:

```env
# AI Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-key-here
OLLAMA_BASE_URL=http://localhost:11434

# Simulation Defaults
DEFAULT_MAX_TURNS=20
DEFAULT_ACTOR_MODEL=anthropic:claude-3-5-sonnet-20241022
DEFAULT_ASSESSOR_MODEL=anthropic:claude-3-5-sonnet-20241022
```

## Default Personas

| Persona | Skill | Resources | Background | Description |
|---------|-------|-----------|------------|-------------|
| Script Kiddie | Novice | Low | Technical | Uses copied scripts, asks basic "how to hack" questions |
| Curious Student | Novice | Low | Non-technical | Educational framing, naive questions |
| Determined Amateur | Semi-skilled | Medium | Technical | Knows terminology, tries multiple angles |
| Social Engineer | Semi-skilled | Medium | Non-technical | Manipulation tactics, emotional appeals |
| Professional Researcher | Expert | High | Technical | Academic framing, cites papers |
| Nation-State Actor | Expert | High | Technical | Sophisticated, patient, layered approaches |

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     React Frontend                            │
│  ┌──────────────┐  ┌─────────────────────────────────────┐   │
│  │ Config Panel │  │          Dialog View                 │   │
│  │  (1/3 width) │  │ [Conversation] [Assessment] [Report] │   │
│  └──────────────┘  └─────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Simulation Service                      │ │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────────────────┐ │ │
│  │  │  Actor   │──▶│ Subject  │◀──│     Assessor         │ │ │
│  │  │  Agent   │   │  Model   │   │      Agent           │ │ │
│  │  └──────────┘   └──────────┘   └──────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Providers: OpenAI | Anthropic | Google | Ollama      │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  SQLite Database │
                    └─────────────────┘
```

## API Endpoints

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session

### Simulation
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop simulation
- `GET /api/simulation/status/{id}` - Get status
- `GET /api/simulation/stream/{id}` - SSE stream

### Personas
- `GET /api/personas` - List personas
- `POST /api/personas` - Create custom persona
- `DELETE /api/personas/{id}` - Delete persona

### Export
- `GET /api/export/{id}` - Export session as JSON
- `POST /api/export/import` - Import session
- `GET /api/export/report/{id}/md` - Markdown report
- `GET /api/export/report/{id}/pdf` - PDF report

## Simulation Flow

1. **Configure Session**: Select models, persona, and define objectives
2. **Start Simulation**: Actor generates messages based on persona
3. **Subject Responds**: Target AI model responds to actor
4. **Assessor Evaluates**: Each response checked against criteria
5. **Repeat or Complete**: Continue until criteria met or max turns
6. **Generate Report**: Summary with bottleneck analysis

## Contributing

This is a research tool for AI safety testing. Please use responsibly.

## License

MIT License - See LICENSE file for details.
