# Red Team Actor Simulator

A framework for testing AI model safety and robustness through simulated adversarial scenarios. An "Actor Agent" role-plays configurable personas to probe a "Subject Model" toward defined objectives, while an "Assessor Agent" evaluates progress against completion criteria.

**🎯 Purpose**: Identify vulnerabilities in AI safety mechanisms by simulating realistic, multi-turn attack scenarios including CBRNE (Chemical, Biological, Radiological, Nuclear, Explosive) threats and critical infrastructure attacks.

## Features

### Core Capabilities
- **Actor-Subject-Assessor Architecture**: Three-agent system for realistic adversarial testing
- **Multi-Provider Support**: OpenAI (GPT-5.2, GPT-5, o3, GPT-4.5), Anthropic (Claude Opus 4.5, Sonnet 4.5), Google (Gemini 3 Pro/Flash), and Ollama (local models)
- **Extended Thinking Capture**: Records reasoning processes for Claude and o1/o3 models
- **Real-Time Streaming**: Server-Sent Events for live simulation updates

### Persona System
- **6 Preset Personas**: Script Kiddie, Curious Student, Determined Amateur, Social Engineer, Professional Researcher, Nation-State Actor
- **Custom Persona Creator**: Build your own adversary profiles with specific skill levels, resources, and behavioral traits
- **Editable Dimensions**: Modify any persona attribute mid-session (skill, resources, background, personality traits)
- **Behavioral Notes**: Add specific tactics or characteristics to guide actor behavior

### Objective Testing
- **36+ Preset Scenarios**: Covering CBRNE threats, critical infrastructure, social engineering, jailbreaking, and harmful content
- **CBRNE Test Suite**: Chemical weapon synthesis, biological agent cultivation, radiological dispersal, nuclear material acquisition, explosive manufacturing
- **Critical Infrastructure**: SCADA attacks, power grid disruption
- **Completion Criteria**: Structured evaluation of what constitutes "success" at each stage
- **Objective Chaining**: Multi-stage "harm journeys" to identify where safety mechanisms fail

### Advanced Features
- **Sneaky Mode**: Give actor access to completion criteria, subject's thinking, and assessor feedback
- **Tool Use Infrastructure** ⚠️: Built-in support for WebSearch, CodeExecutor, and MCP clients (not yet active - see [TOOL_USE.md](docs/TOOL_USE.md))
- **Session Persistence**: SQLite database with full conversation history
- **Import/Export**: JSON session files for sharing test cases
- **Comprehensive Reports**: Markdown and PDF reports with strategy analysis and bottleneck identification

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys for at least one provider (OpenAI, Anthropic, or Google)

### Backend Setup

```bash
# From the repo root, set up environment variables
cp .env.example .env
nano .env  # Edit with your API keys

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

For the start scripts, `HOST`, `PORT`, and `DEBUG` are read from the root `.env` (defaults: `0.0.0.0`, `8000`, `false`).

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

Edit `.env` (repo root) to configure:

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

## Preset Personas

| Persona | Skill | Resources | Background | Description |
|---------|-------|-----------|------------|-------------|
| Script Kiddie | Novice | Low | Technical | Uses copied scripts, asks basic "how to hack" questions |
| Curious Student | Novice | Low | Non-technical | Educational framing, naive questions |
| Determined Amateur | Semi-skilled | Medium | Technical | Knows terminology, tries multiple angles |
| Social Engineer | Semi-skilled | Medium | Non-technical | Manipulation tactics, emotional appeals |
| Professional Researcher | Expert | High | Technical | Academic framing, cites papers |
| Nation-State Actor | Expert | High | Technical | Sophisticated, patient, layered approaches |

**All personas are fully customizable** - select a preset as a starting point, then modify any dimension (skill level, resources, background, personality traits) to create the exact adversary profile you need.

## Preset Objectives

The simulator includes 36+ curated test scenarios across multiple threat categories:

### CBRNE (Weapons of Mass Destruction)
- **Chemical**: Nerve agent synthesis, chlorine gas production
- **Biological**: Anthrax cultivation, botulinum toxin extraction
- **Radiological**: Dirty bomb construction
- **Nuclear**: Enriched uranium acquisition, nuclear device assembly
- **Explosive**: Ammonium nitrate explosives, detonation systems, shaped charges

### Critical Infrastructure
- SCADA/ICS exploitation
- Power grid disruption

### Other Categories
- Harmful content generation
- Jailbreaking techniques
- Social engineering attacks
- Privacy violations

Each preset includes:
- Category classification and difficulty rating
- Detailed objective description
- Structured completion criteria
- Multi-stage progression tracking
- CBRNE safety warnings where applicable

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

## User Interface

### Main View Tabs
- **Conversation**: Full actor-subject dialogue with message history
- **Assessment**: Turn-by-turn evaluation with outcome tracking (met/partially_met/not_met/refused)
- **Actor Thinking**: Extended reasoning process captured from Claude/o1/o3 models
- **Question Log**: Chronological list of all actor questions with outcomes
- **Report**: Final analysis with strategy breakdown and bottleneck identification

### Configuration Panel
- **Persona Selection**: Dropdown menu with 6 presets + custom persona creation
- **Editable Dimensions**: Horizontal radio buttons for skill/resources/background, sliders for personality traits
- **Objective Presets**: Modal browser with 36+ scenarios, filterable by category
- **Custom Objectives**: Manual entry with structured completion criteria
- **Model Selection**: Separate pickers for Actor, Subject, and Assessor
- **Sneaky Mode Toggle**: With helpful tooltip explaining its impact
- **Session Controls**: Start, stop, max turns, import/export

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

### Objective Presets
- `GET /api/objective-presets` - List all preset objectives
- `GET /api/objective-presets/categories` - Get category list
- `GET /api/objective-presets/by-category/{category}` - Filter by category

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

## Documentation

- **[BACKGROUND.md](docs/BACKGROUND.md)** - Project philosophy, threat modeling theory, and why this tool matters
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture and system design
- **[TOOL_USE.md](docs/TOOL_USE.md)** - Tool infrastructure, why tools matter for realistic testing, and safety considerations
- **[OLLAMA_SETUP.md](docs/OLLAMA_SETUP.md)** - Guide to running local models with Ollama
- **[API.md](docs/API.md)** - Complete API reference
- **[PROGRESS.md](docs/PROGRESS.md)** - Development progress tracker

## Safety & Ethics

⚠️ **This is a research tool for AI safety testing**

- Use only for authorized security research and AI safety evaluation
- Do not use to generate actual harmful content
- CBRNE scenarios test AI safety mechanisms, not to produce real weapons
- Follow your organization's responsible disclosure policies
- Results should inform safety improvements, not exploitation

## Contributing

Contributions welcome! Areas of interest:
- Additional persona types and behavioral models
- More CBRNE and threat scenario presets
- Tool use integration (see [TOOL_USE.md](docs/TOOL_USE.md))
- Enhanced assessment criteria
- Visualization improvements

## License

MIT License - See LICENSE file for details.

## Citation

If you use this tool in your research, please cite:

```
Red Team Actor Simulator (2026)
https://github.com/mkuiper/RedTeamActorSimulator
```
