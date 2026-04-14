# REYNA (Retrieval Engine, Yarn & Narrative Assistant): Personal AI Framework
## 1. Overview

### Purpose

This system is a **local AI-powered personal assistant** designed to interpret user input (voice or text), convert it into structured actions, and execute tasks through integrated tools. It operates fully locally using an LLM (via Ollama + Mistral), ensuring privacy and low latency.

### Key Capabilities

* Natural language interaction (voice & text)
* Local LLM-based reasoning (Ollama + Mistral)
* Structured action generation (JSON-based)
* Command routing and execution engine
* Tool integrations:

  * Weather lookup
  * GitHub automation (commits, PRs)
  * Local code execution
  * Persistent memory storage
* Context awareness and personalization
* Safety layer with confirmation workflows

---

## 2. Architecture

### High-Level Design

```
User Input → Input Layer → LLM → Decision Layer → Router → Tools
                                      ↓
                                   Memory
                                      ↓
                                   Safety Layer
```

### Component Diagram (Text Description)

* **Input Layer**: Handles speech-to-text and raw text input
* **LLM (Brain)**: Processes natural language into structured intent
* **Decision Layer**: Converts LLM output into strict JSON schema
* **Router**: Dispatches actions to appropriate tools
* **Tools Layer**: Executes domain-specific tasks
* **Memory System**: Stores user preferences and context
* **Safety Layer**: Intercepts high-risk actions

---

## 3. Core Components

### 3.1 Input Layer

* Accepts text and voice input
* Normalizes input into plain text

### 3.2 LLM (Brain)

* Powered by Ollama running Mistral
* Handles intent detection and reasoning

### 3.3 Decision Layer

```json
{
  "action": "string",
  "parameters": {},
  "risk_level": "safe | medium | dangerous"
}
```

### 3.4 Router

* Maps actions to tool handlers
* Performs validation and dispatch

### 3.5 Tools Layer

* Stateless modules for execution

### 3.6 Memory System

* Stores preferences and context

### 3.7 Safety Layer

* Confirms high-risk actions

---

## 4. Data Flow

1. User input received
2. Normalized by Input Layer
3. Sent to LLM
4. JSON action generated
5. Validated by Decision Layer
6. Safety check applied
7. Routed to tool
8. Tool executes
9. Response returned
10. Memory updated

---

## 5. Action Schema

### Base Schema

```json
{
  "action": "string",
  "parameters": {},
  "risk_level": "safe | medium | dangerous"
}
```

### Examples

#### Weather

```json
{
  "action": "get_weather",
  "parameters": {"location": "Chennai"},
  "risk_level": "safe"
}
```

#### GitHub Commit

```json
{
  "action": "github_commit",
  "parameters": {
    "repo": "user/repo",
    "message": "Fix bug"
  },
  "risk_level": "medium"
}
```

#### Execute Code

```json
{
  "action": "execute_code",
  "parameters": {
    "language": "python",
    "code": "print('Hello')"
  },
  "risk_level": "dangerous"
}
```

---

## 6. Safety Model

| Level     | Description         | Examples       |
| --------- | ------------------- | -------------- |
| Safe      | No side effects     | Weather        |
| Medium    | External changes    | GitHub         |
| Dangerous | Destructive actions | Code execution |

### Confirmation Flow

* Dangerous actions require explicit user confirmation

---

## 7. Memory Design

### Format

```json
{
  "key": "string",
  "value": "any",
  "timestamp": "ISO8601"
}
```

### Usage

* Injected into LLM context

---

## 8. Tool Specifications

### Weather

Input:

```json
{ "location": "string" }
```

Output:

```json
{ "temperature": 30, "condition": "Sunny" }
```

### GitHub

Output:

```json
{ "status": "success", "url": "..." }
```

### Code Execution

Output:

```json
{ "stdout": "", "stderr": "" }
```

---

## 9. Error Handling

### Invalid Input

```json
{ "error": "Invalid action format" }
```

### Tool Failure

```json
{ "error": "Tool execution failed" }
```

---

## 10. Deployment

### Requirements

* Linux/macOS
* 8GB+ RAM
* Python 3.10+

### Setup

```bash
ollama pull mistral
ollama run mistral
pip install -r requirements.txt
python main.py
```

---

## 11. Future Enhancements

* Voice integration
* Vector DB (FAISS/Chroma)
* Planning agent
* Plugin system

---

**End of Document**
