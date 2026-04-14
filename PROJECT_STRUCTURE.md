# Project Structure

This project has been reorganized for improved readability and maintainability.

## Directory Layout

```
R.E.Y.N.A/
├── src/                          # Core application modules
│   ├── __init__.py
│   ├── main.py                   # Entry point and main loop
│   ├── llm.py                    # LLM integration and action generation
│   ├── router.py                 # Action routing and execution
│   ├── memory.py                 # Memory system with vector DB
│   ├── schema.py                 # Pydantic data models
│   ├── diagnostics.py            # Diagnostics and health checks
│   └── reyna_bridge.py           # OpenClaw Reyna bridge IPC
│
├── tools/                        # Tool implementations
│   ├── __init__.py
│   ├── execute_code.py           # Code execution tool
│   ├── github.py                 # GitHub integration tool
│   └── weather.py                # Weather API tool
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_main_flow.py         # End-to-end flow tests
│   ├── test_llm.py               # LLM generation tests
│   ├── test_integration.py       # Integration tests
│   ├── test_bridge_mode.py       # Bridge mode tests
│   └── test_openclaw.py          # OpenClaw CLI tests
│
├── docs/                         # Documentation
│   ├── readme.md                 # Main documentation
│   ├── BRIDGE_FIX_DETAILS.md     # Bridge implementation details
│   └── OPENCLAW_INTEGRATION.md   # OpenClaw integration guide
│
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── PROJECT_STRUCTURE.md          # This file
```

## Running the Project

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the main application:
```bash
python -m src.main
```

### Run tests:
```bash
python -m pytest tests/
# or individual test:
python tests/test_main_flow.py
```

## Module Descriptions

### Core Modules (src/)

- **main.py**: Interactive REYNA loop, handles user input
- **llm.py**: Integrates with LLM (Ollama/OpenClaw) for action generation
- **router.py**: Routes generated actions to appropriate tools with safety checks
- **memory.py**: Manages short-term history, context, and vector embeddings
- **schema.py**: Pydantic models for type safety (ActionSchema)
- **diagnostics.py**: System health checks and bridge connectivity
- **reyna_bridge.py**: File-based IPC for OpenClaw Reyna agent

### Tools (tools/)

- **execute_code.py**: Safely executes code snippets
- **github.py**: GitHub API integration
- **weather.py**: Weather data fetching

### Tests (tests/)

Test files validate different aspects of the system:
- Core LLM integration
- End-to-end workflows
- Tool execution and routing
- OpenClaw bridge connectivity

## Import Patterns

### In src/ modules:
Use relative imports:
```python
from .memory import memory
from .schema import ActionSchema
```

### In test files:
Tests add src to sys.path:
```python
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from llm import generate_action
```
