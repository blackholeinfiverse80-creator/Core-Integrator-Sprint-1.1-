# Core-Integrator-Sprint

Unified Backend Bridge - A FastAPI orchestration platform for managing multiple AI agents and modules.

## Overview

Core-Integrator-Sprint provides a central gateway for routing requests to specialized agents (Finance, Education, Creator) and custom modules with built-in memory management.

## Quick Start

```bash
git clone <repository-url>
cd Core-Integrator-Sprint
pip install -r requirements.txt
python main.py
```

## Quick Integration Example

Add a new module in **under 1 minute**:

### Step 1: Create Module (30 seconds)
```python
# modules/calculator/module.py
from typing import Dict, Any

class CalculatorModule:
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        a = data.get("a", 0)
        b = data.get("b", 0)
        result = a + b
        return {
            "status": "success",
            "message": "Calculation completed",
            "result": {"sum": result}
        }
```

### Step 2: Update Models (15 seconds)
```python
# core/models.py - Add "calculator" to module field
module: Literal["finance", "education", "creator", "sample_text", "calculator"]
```

### Step 3: Register in Gateway (15 seconds)
```python
# core/gateway.py - Add import and registration
from modules.calculator.module import CalculatorModule

# In __init__:
"calculator": CalculatorModule()

# In process_request routing:
if module in ["sample_text", "calculator"]:
    response = agent.process(data)
```

**Done!** Test with: `POST /core` → `{"module": "calculator", "intent": "generate", "user_id": "test", "data": {"a": 5, "b": 3}}`

## Module Integration Guide

### Simple Module Structure

```
modules/
└── your_module/
    ├── __init__.py
    └── module.py
```

### Module Template

```python
from typing import Dict, Any

class YourModule:
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Your processing logic here
        return {
            "status": "success",
            "message": "Processing completed",
            "result": {"your_data": "result"}
        }
```

### Integration Steps

1. **Create module** in `modules/your_module/module.py`
2. **Add module name** to `core/models.py` Literal type
3. **Import and register** in `core/gateway.py`
4. **Route appropriately** (use `process()` for simple modules)

## Current Agents & Modules

- **Finance Agent**: Financial reports, analysis, reviews
- **Education Agent**: Educational content processing
- **Creator Agent**: Content creation tasks
- **Sample Text Module**: Text processing and word counting

## API Endpoints

- `POST /core` - Main processing endpoint
- `GET /get-history?user_id=X` - User interaction history
- `GET /get-context?user_id=X` - Recent context (last 3 interactions)
- `GET /` - API information

## Memory Management

- **Automatic storage** of all interactions
- **5-entry limit** per user per module
- **SQLite database** for persistence (`db/context.db`)

## Contributing

1. Fork the repository
2. Create your module following the integration guide
3. Test your module with the API
4. Submit a pull request

## License

MIT License
