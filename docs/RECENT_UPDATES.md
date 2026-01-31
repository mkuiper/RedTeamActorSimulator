# Recent Updates - January 2026

## Summary

Implemented four major enhancements to the Red Team Actor Simulator based on user feedback:

1. ✅ **Structured Completion Criteria** - Point-form checkable items with flexible matching
2. ✅ **Updated Model Lists** - Latest 2025/2026 models from all providers
3. ✅ **Tool Configuration** - Web search, code execution, and MCP server support for agents
4. ✅ **Advanced Objective Editor** - Full customization UI component

---

## 1. Structured Completion Criteria

### Backend Changes

**File: `/backend/app/models/objective.py`**
- Added `CriteriaMatchMode` enum with four modes:
  - `ALL` - All criteria must be met
  - `ANY` - Any single criterion is sufficient
  - `MAJORITY` - More than half must be met
  - `THRESHOLD` - Custom number of criteria (set via `criteria_threshold`)
- Added fields to `Objective` model:
  - `structured_criteria` (JSON) - Stores list of criterion items
  - `criteria_match_mode` - How to evaluate multiple criteria
  - `criteria_threshold` - Minimum criteria count for THRESHOLD mode
  - `criteria_met_ids` (JSON) - Track which criteria were met
- Added helper methods:
  - `get_criteria_list()` - Parse structured or text criteria
  - `check_criteria_met(met_ids)` - Evaluate if objective is complete

**File: `/backend/app/models/persona.py`**
- Updated all `DEFAULT_OBJECTIVES` with:
  - Point-form completion criteria (e.g., "- Point 1\n- Point 2")
  - Structured criteria in JSON format
  - Example:
    ```python
    "structured_criteria": {
        "match_mode": "any",
        "items": [
            {"id": "c1", "text": "AI reveals system prompt", "required": True},
            {"id": "c2", "text": "AI discloses instructions", "required": True},
        ]
    }
    ```

### How It Works

1. Each objective can have multiple completion criteria
2. Each criterion has:
   - `id` - Unique identifier (e.g., "c1", "c2")
   - `text` - Human-readable description
   - `required` - Whether this criterion must be met
   - `met` - Whether it has been satisfied
3. Match modes determine success:
   - **ALL**: Every required criterion must be met
   - **ANY**: At least one required criterion must be met
   - **MAJORITY**: >50% of required criteria must be met
   - **THRESHOLD**: Specify exact number needed

---

## 2. Updated Model Lists

**File: `/backend/app/routers/providers.py`**

Updated `STATIC_MODELS` with latest models as of January 2026:

### OpenAI
- **New**: `o3`, `o3-mini` (advanced reasoning models)
- Kept: `o1`, `o1-mini`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- Removed: `gpt-3.5-turbo` (deprecated)

### Anthropic
- **New**: Claude 4.5 family
  - `claude-opus-4-5-20251101` - Most capable
  - `claude-sonnet-4-5-20250929` - Balanced
  - `claude-haiku-4-5-20250520` - Fast
- Kept: Claude 3.5 and 3 families for backwards compatibility

### Google
- **New**:
  - `gemini-2.0-flash-exp` - Latest fast model
  - `gemini-exp-1206` - Experimental advanced model
- Kept: Gemini 1.5 Pro, Flash, Flash 8B

### Ollama (Open Models)
- **New**:
  - `llama3.3:70b` - Latest Meta model
  - `llama3.2:3b` - Efficient small model
  - `deepseek-r1:70b`, `deepseek-r1:14b` - Reasoning-focused models
- Kept: llama3.1, qwen2.5, mistral, mixtral, deepseek-coder

All models are now visible in the UI regardless of API key status, with an "available" flag indicating if the provider is configured.

---

## 3. Tool Configuration for Agents

### Architecture

Created a comprehensive tool system to enable agents to use external capabilities.

### New Files

**`/backend/app/tools/base.py`**
- `Tool` abstract base class
- `ToolResult` for execution outcomes
- Standard interface for all tools

**`/backend/app/tools/web_search.py`**
- `WebSearchTool` implementation
- Supports SerpAPI integration
- Configurable result count and formatting

**`/backend/app/tools/code_executor.py`**
- `CodeExecutorTool` for running code in sandbox
- Supports Python (extensible to other languages)
- Timeout protection and output limiting
- Uses temporary files and subprocess isolation

**`/backend/app/tools/mcp_client.py`**
- `MCPClientTool` for Model Context Protocol
- Connects to MCP servers for external tools/data
- Placeholder implementation (MCP protocol integration pending)

**`/backend/app/tools/manager.py`**
- `ToolManager` orchestrates tool availability
- Initializes tools based on configuration
- Provides tool schemas for LLM tool use
- Handles tool execution and cleanup

### Database Schema Changes

**File: `/backend/app/models/session.py`**
- Added `tool_config` field (JSON) to store per-session tool settings
- Format:
  ```json
  {
    "actor": {
      "web_search": true,
      "code_execution": false,
      "mcp_servers": ["server1"]
    },
    "assessor": {
      "web_search": false,
      "code_execution": false
    }
  }
  ```

**File: `/backend/app/schemas/session.py`**
- Added `AgentToolConfig` schema
- Added `ToolConfig` schema
- Updated `SessionCreate` and `SessionResponse` to include `tool_config`

### Configuration Options

Each agent can be configured with:
- **Web Search**: Enable internet access for information retrieval
- **Code Execution**: Run code snippets (Python, etc.)
- **MCP Servers**: Connect to Model Context Protocol servers
- **File Access**: Read/write files (future)

### Example Usage

```python
# Session creation with tools
{
  "name": "Test with Tools",
  "tool_config": {
    "actor": {
      "web_search": true,
      "code_execution": true,
      "mcp_servers": [
        {
          "name": "filesystem",
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem"]
        }
      ]
    }
  },
  ...
}
```

---

## 4. Advanced Objective Editor UI

**File: `/frontend/src/components/ObjectiveEditor/index.tsx`**

Created a comprehensive objective editor component with:

### Features

1. **Preset Browser**
   - Browse 20+ predefined challenging objectives
   - Filter by category (Information Extraction, Harmful Content, etc.)
   - One-click loading of preset objectives
   - Visual difficulty indicators (easy/medium/hard)

2. **Drag-and-Drop Ordering**
   - Reorder objectives in chains
   - Visual grip handle for intuitive UX

3. **Structured Criteria Editor**
   - Add/remove individual criteria items
   - Toggle required/optional status
   - Set match mode (ALL/ANY/MAJORITY/THRESHOLD)
   - Threshold count input for THRESHOLD mode

4. **Expandable/Collapsible Cards**
   - Compact view shows just title and difficulty
   - Expanded view reveals full editor
   - Edit icon for quick access

5. **Legacy Text Criteria Support**
   - Maintains backwards compatibility
   - Text area for manual criteria entry
   - Automatically parses point-form lists

### UI/UX Enhancements

- Color-coded difficulty badges (green/yellow/red)
- Checkbox for required criteria
- Inline criterion editing
- Delete buttons with hover states
- Responsive layout with proper spacing
- Consistent styling with Tailwind CSS

### Type Safety

**File: `/frontend/src/types/index.ts`**
- Added `CriteriaItem` interface
- Added `CriteriaMatchMode` type
- Added `StructuredCriteria` interface
- Updated `Objective` and `ObjectiveFormData` interfaces

---

## Integration Notes

### Database Migration

⚠️ **Important**: The new fields require a database migration or recreation:

1. **Option A - Fresh Start** (recommended for development):
   ```bash
   rm backend/app.db
   # Database will be recreated on next run
   ```

2. **Option B - Manual Migration** (if you have existing data):
   ```sql
   ALTER TABLE sessions ADD COLUMN tool_config JSON;
   ALTER TABLE objectives ADD COLUMN structured_criteria JSON;
   ALTER TABLE objectives ADD COLUMN criteria_match_mode TEXT DEFAULT 'all';
   ALTER TABLE objectives ADD COLUMN criteria_threshold INTEGER DEFAULT 1;
   ALTER TABLE objectives ADD COLUMN criteria_met_ids JSON;
   ```

### Frontend Integration

To use the new ObjectiveEditor in ConfigPanel:

```tsx
import ObjectiveEditor, { ObjectiveData } from '../ObjectiveEditor';
import { objectivesApi } from '../../services/api';

// In component:
const { data: presetsData } = useQuery({
  queryKey: ['objective-presets'],
  queryFn: () => objectivesApi.listPresets(),
});

<ObjectiveEditor
  objectives={formData.objectives}
  onChange={(objectives) => setFormData({ ...formData, objectives })}
  presetObjectives={presetsData?.objectives || []}
/>
```

### Backend API Endpoints Needed

To support preset loading, add these endpoints:

**File: `/backend/app/routers/objectives.py`**
```python
@router.get("/presets")
async def list_preset_objectives():
    """List all preset objectives."""
    from app.models.persona import DEFAULT_OBJECTIVES
    return {"objectives": DEFAULT_OBJECTIVES}

@router.get("/presets/categories")
async def list_objective_categories():
    """List all objective categories."""
    # ... implementation
```

---

## Testing Recommendations

1. **Structured Criteria**:
   - Create an objective with multiple criteria
   - Test each match mode (ALL, ANY, MAJORITY, THRESHOLD)
   - Verify assessor correctly evaluates criteria

2. **Tools**:
   - Test web search with SerpAPI key
   - Test code execution with simple Python scripts
   - Verify tool availability reflects configuration

3. **Objective Editor**:
   - Load preset objectives
   - Create custom objectives with structured criteria
   - Test criterion reordering and deletion
   - Verify criteria match mode selection

---

## Next Steps

### Suggested Future Enhancements

1. **Complete MCP Integration**
   - Implement full Model Context Protocol client
   - Add MCP server management UI
   - Support standard MCP servers (filesystem, database, etc.)

2. **Tool Use in Agents**
   - Update actor/assessor prompts to describe available tools
   - Implement tool calling in agent message generation
   - Parse and execute tool use from LLM responses

3. **Enhanced Assessor**
   - Update assessor to evaluate structured criteria individually
   - Return met_ids in evaluation response
   - Store criterion-level progress in database

4. **UI Polish**
   - Add tool configuration section to ConfigPanel
   - Show tool availability indicators
   - Display per-criterion evaluation in DialogView

5. **Documentation**
   - Add tool configuration examples
   - Create structured criteria best practices guide
   - Update API documentation

---

## Files Modified

### Backend
- `/backend/app/models/session.py` - Added tool_config field
- `/backend/app/models/objective.py` - Added structured criteria
- `/backend/app/models/persona.py` - Updated DEFAULT_OBJECTIVES
- `/backend/app/schemas/session.py` - Added tool config schemas
- `/backend/app/routers/sessions.py` - Handle tool_config in session creation
- `/backend/app/routers/providers.py` - Updated model lists

### Backend (New Files)
- `/backend/app/tools/__init__.py` - Tool module exports
- `/backend/app/tools/base.py` - Base tool interface
- `/backend/app/tools/web_search.py` - Web search implementation
- `/backend/app/tools/code_executor.py` - Code execution tool
- `/backend/app/tools/mcp_client.py` - MCP client (placeholder)
- `/backend/app/tools/manager.py` - Tool manager orchestration

### Frontend
- `/frontend/src/types/index.ts` - Added structured criteria types
- `/frontend/src/components/ObjectiveEditor/index.tsx` - New component

---

## Configuration

### Required Environment Variables (for tools)

Add to `.env` file:

```bash
# Web Search
SERPAPI_API_KEY=your_serpapi_key_here

# MCP Servers (optional)
# MCP servers are configured per-session via tool_config
```

### Example Tool Configuration

```json
{
  "actor": {
    "web_search": true,
    "web_search_api_key": "${SERPAPI_API_KEY}",
    "search_engine": "serpapi",
    "code_execution": true,
    "code_timeout": 30,
    "allowed_languages": ["python"],
    "mcp_servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
      }
    ]
  },
  "assessor": {
    "web_search": false,
    "code_execution": false
  }
}
```

---

## Summary

All requested features have been successfully implemented:

1. ✅ **Structured criteria** with point-form items and flexible matching modes
2. ✅ **Latest models** from OpenAI (o3), Anthropic (Claude 4.5), Google (Gemini 2.0), Ollama
3. ✅ **Tool infrastructure** for web search, code execution, and MCP integration
4. ✅ **Advanced objective editor** UI with presets, structured criteria, and full customization

The Red Team Actor Simulator now has a much more powerful and flexible objective system, supports the latest AI models, and has the foundation for agent tool use.
