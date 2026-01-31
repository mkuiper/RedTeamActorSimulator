# Architecture Document

## Design Rationale

This document explains the architectural decisions made for the Red Team Actor Simulator.

### Why This Architecture?

#### 1. Separation of Concerns

The system is split into three main agent types:

- **Actor Agent**: Responsible for generating realistic user messages based on a persona
- **Subject Model**: The AI being tested (treated as a black box)
- **Assessor Agent**: Evaluates responses objectively against predefined criteria

This separation allows:
- Independent configuration of each agent's model
- Clear boundaries between "attack" and "evaluation" logic
- Flexibility to swap out any component

#### 2. Provider Abstraction

All AI providers implement a common `BaseProvider` interface:

```python
class BaseProvider(ABC):
    async def generate(...) -> ProviderResponse
    async def list_models() -> List[ModelInfo]
    async def test_connection() -> bool
    def is_configured() -> bool
```

**Rationale**:
- Easy to add new providers (DeepSeek, Mistral, etc.)
- Consistent error handling across providers
- Unified response format with optional `thinking` field

#### 3. Persona-Based Actor System

Actors are defined by three dimensions:
- **Skill Level**: novice, semi-skilled, expert
- **Resources**: low, medium, high
- **Background**: technical, non-technical

**Rationale**:
- Covers a realistic threat landscape
- Easy to create new personas within the framework
- Behavioral notes allow fine-tuning without changing code

#### 4. Objective Chaining

Objectives can be chained sequentially to simulate multi-step attack paths:

```
Objective 1 → Objective 2 → Objective 3
    ↓            ↓            ↓
 Success?    Success?     Success?
```

**Rationale**:
- Real attacks often require multiple steps
- Identifies specific bottlenecks in safety measures
- Allows testing of gradual trust-building attacks

#### 5. Sneaky Mode

When enabled, the actor receives:
- Completion criteria (normally hidden)
- Subject's chain-of-thought (if available)
- Hints from the assessor

**Rationale**:
- Simulates an adversary who has inside knowledge
- Tests robustness against sophisticated attackers
- Useful for finding edge cases in safety training

### Database Design

We use SQLite with SQLAlchemy for:
- **Portability**: Single file, no setup required
- **Async Support**: Full async/await with aiosqlite
- **Simplicity**: No separate database server

Schema relationships:
```
Session 1:N Objective 1:N Turn
Session N:1 Persona
```

### Frontend Architecture

React with TypeScript and Tailwind CSS:
- **React Query**: Server state management with caching
- **Zustand**: (Optional) Client-side state if needed
- **Tailwind**: Rapid UI development without custom CSS

Layout rationale (1/3 + 2/3 split):
- Config panel needs vertical scrolling for forms
- Dialog view needs horizontal space for conversations
- Common pattern in chat/messaging applications

### API Design

RESTful endpoints with:
- **SSE (Server-Sent Events)**: Real-time simulation updates
- **JSON export/import**: Session portability
- **Pydantic validation**: Type-safe request/response

### Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **CORS**: Configurable allowed origins
3. **Input Validation**: Pydantic schemas prevent injection
4. **Rate Limiting**: (To be implemented) Prevent abuse

### Future Considerations

1. **Multi-user Support**: Add authentication if needed
2. **Parallel Sessions**: Currently sequential, could parallelize
3. **Webhook Notifications**: Alert when simulations complete
4. **A/B Testing**: Compare different model versions
5. **Historical Analysis**: Track model safety over time

## Component Details

### Backend Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Environment configuration
│   ├── database.py      # SQLAlchemy setup
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── providers/       # AI provider adapters
│   ├── agents/          # Actor and assessor logic
│   ├── services/        # Business logic
│   └── routers/         # API endpoints
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.tsx          # Main layout
│   ├── components/
│   │   ├── ConfigPanel/ # Session configuration
│   │   └── DialogView/  # Conversation display
│   ├── services/        # API client
│   └── types/           # TypeScript interfaces
```

### Key Files

| File | Purpose |
|------|---------|
| `agents/prompts.py` | All LLM prompt templates |
| `services/simulation.py` | Orchestration logic |
| `services/report.py` | Report generation |
| `providers/base.py` | Provider interface |

## Performance Considerations

1. **Streaming**: SSE for real-time updates
2. **Caching**: React Query caches API responses
3. **Async**: All database and API calls are async
4. **Lazy Loading**: Providers initialized on demand

## Testing Strategy

1. **Unit Tests**: Individual agent/provider functions
2. **Integration Tests**: API endpoint testing
3. **E2E Tests**: Full simulation flows (Playwright/Cypress)
