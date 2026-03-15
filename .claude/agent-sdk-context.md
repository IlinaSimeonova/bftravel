# Agent SDK Developer Context

**Purpose:** Shared context for all developers working on Agent SDK-related Jira tasks.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Core Files Reference](#3-core-files-reference)
4. [MCP Tools (13 Total)](#4-mcp-tools-13-total)
5. [Execution Flow](#5-execution-flow)
6. [API Endpoints](#6-api-endpoints)
7. [Database Models](#7-database-models)
8. [Worker Queue System](#8-worker-queue-system)
9. [Session Persistence](#9-session-persistence)
10. [Security & Resource Limits](#10-security--resource-limits)
11. [WebSocket Real-Time Updates](#11-websocket-real-time-updates)
12. [System Prompt Architecture](#12-system-prompt-architecture)
13. [Code Patterns (Critical)](#13-code-patterns-critical)
14. [Testing & Debugging](#14-testing--debugging)
15. [Related Specifications](#15-related-specifications)

---

## 1. Overview

The **Claude Agent SDK** is the AI agent that builds and modifies workflows using MCP tools.

### What the Agent Does

- **Builds workflows** from user requests (creates nodes, writes code)
- **Modifies existing workflows** (fixes bugs, adds features)
- **Tests workflows** autonomously (runs tests, diagnoses failures)
- **Iterates until working** (fix → test → repeat)

---

## 2. Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│   User types: "Fix the email parsing bug"                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DJANGO API                                │
│   POST /api/automation/workflows/<id>/agent-sdk/execute/        │
│   → Creates AsyncOperation → Queues to SQS                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SQS AGENT QUEUE                             │
│   bigbongo-{env}-agent-queue (concurrency: 3)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOCKER WORKER                                │
│   Picks up task → Calls AgentSDKService.execute_agent()         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLAUDE AGENT SDK                               │
│                                                                  │
│   ┌────────────────────────────────────────┐                    │
│   │     AGENT LOOP                         │                    │
│   │  1. Send message to Claude API         │                    │
│   │  2. Claude responds with tool calls    │◄────────┐          │
│   │  3. Execute MCP tool (DB operation)    │         │          │
│   │  4. Return result to Claude            │─────────┘          │
│   │  5. Repeat until done                  │                    │
│   └────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE                                    │
│   Node, CodeVersion, Workflow models updated                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Files Reference

### Core Service Files

| File | Purpose | Key Functions/Classes |
|------|---------|----------------------|
| `automation/services/agent_sdk_service.py` | **Main orchestrator** | `AgentSDKService.execute_agent()`, `build_system_prompt()` |
| `automation/services/agent_mcp_tools.py` | **13 MCP tools** | `create_workflow_mcp_server()` |
| `automation/services/workflow_context_service.py` | Context builder | `get_workflow_basic_context()`, `get_nodes_context()` |
| `automation/services/async_llm_service.py` | Operation handler routing | `AgentOperationHandler.execute()` |
| `automation/api_views_agent_sdk.py` | REST API endpoints | `agent_sdk_execute()`, `agent_sdk_build_workflow()` |
| `automation/prompts/bigbongo_context.md` | System prompt context | - |

### Worker System

| File | Purpose |
|------|---------|
| `workers/docker-compose.workers.yml` | Base worker config (4 queues) |
| `workers/docker-compose.workers.local.yml` | Local dev overrides |
| `workers/docker-compose.workers.prod.yml` | Production settings |
| `automation/services/task_router.py` | Routes tasks to queues |
| `automation/services/sqs_service.py` | AWS SQS interactions |
| `automation/management/commands/run_sqs_worker.py` | Worker command |

### Frontend

| File | Purpose |
|------|---------|
| `automation/static/automation/js/async-operations.js` | `window.AsyncOps` for agent calls |
| `recorder/consumers.py` | WebSocket handlers |

---

## 4. MCP Tools (13 Total)

### Tool Summary Table

| # | Tool | Purpose | New/Improved |
|---|------|---------|--------------|
| 1 | `get_workflow_context` | Full workflow + all nodes with code | - |
| 2 | `list_nodes` | List nodes with basic info | - |
| 3 | `check_workflow_credentials` | Verify credentials work | ✨ NEW |
| 4 | `get_node_code` | Get code for specific node | - |
| 5 | `update_node_code` | Update code (versioned) | 🔧 +WebSocket |
| 6 | `get_node_schema` | Get input/output schemas | - |
| 7 | `update_node_schema` | Update schemas | 🔧 +WebSocket |
| 8 | `execute_workflow_test` | Run workflow test | 🔧 Better errors |
| 9 | `get_node_execution_data` | Drill down into large data | ✨ NEW |
| 10 | `modify_interface` | Update workflow UI | 🔧 Now sync |
| 11 | `modify_workflow_flow` | Add/remove skip conditions | 🔧 +WebSocket |
| 12 | `create_workflow_nodes` | Batch create all nodes | ✨ NEW |
| 13 | `modify_workflow_nodes` | Batch update/remove/add | ✨ NEW |
| 14 | `inspect_document_structure` | Analyze doc structure before fill code | ✨ NEW |

### Tool Details

#### `get_workflow_context`
Returns full workflow JSON with all nodes, code, schemas. Agent's first call typically.

#### `check_workflow_credentials` (NEW)
Verifies credentials before running workflows:
- Scans code for `get_credential()` calls
- Checks if each integration is connected
- Tests connectivity by calling `CredentialService.get_credential()`

#### `create_workflow_nodes` (NEW - BATCH)
Creates ALL workflow nodes in a SINGLE call:
- Nested structure support (container + action nodes)
- Pre-generated UUIDs for `input_mappings` references
- Auto-generates interface after creating nodes

#### `modify_workflow_nodes` (NEW - BATCH)
Batch operations on existing workflows:
- `update` - Change code, name, schemas
- `remove` - Delete node
- `add` - Create new node

#### `execute_workflow_test`
Runs workflow with test inputs:
- Returns execution results + errors
- Sends WebSocket notifications for step status
- Large response handling with hints to use `get_node_execution_data`

#### `get_node_execution_data` (NEW)
Four modes for inspecting large execution data:
1. **Summary** - Sizes and metadata
2. **Structure** - Keys only (no values)
3. **Search** - Find pattern with context
4. **Read Chunk** - Paginated read

#### `inspect_document_structure` (NEW)
Analyzes a document's internal structure before writing fill/modification code:
- **DOCX**: Tables (label-value layout detection), `{{placeholder}}` patterns, content controls, inline patterns, headings
- **XLSX/CSV**: Sheet names, headers, row counts, sample data
- **PDF**: Page count, AcroForm fields, text preview
- **PPTX**: Slides, placeholders, text frames
- Returns `fill_strategy` for DOCX: `table_label_value`, `placeholder`, `content_control`, `inline_pattern`, or `mixed`

---

## 5. Execution Flow

### Typical Agent Task Flow

```
User: "Fix the bug in the email parsing node"
         ↓
Agent receives:
  - System prompt (BigBongo context + workflow ID + tool docs)
  - Task: "Fix the bug in the email parsing node"
         ↓
Agent actions:
  1. get_workflow_context() → understands all nodes
  2. get_node_code(email_parsing_node) → sees current code
  3. Analyzes, finds bug
  4. update_node_code(email_parsing_node, fixed_code)
  5. execute_workflow_test({test_inputs}) → verifies fix
  6. If fails: analyze error, fix again, test again
  7. Done when test passes
```

### Build Mode Flow (New Workflows)

```
LLM Call 1: PLAN
  Agent returns 3x parallel create_workflow_nodes calls
  → All nodes created instantly

LLM Call 2: TEST
  Agent calls execute_workflow_test
  → Verifies workflow works

LLM Call 3+: FIX (if needed)
  Agent iterates until passing
```

---

## 6. API Endpoints

### Execute Agent SDK
```
POST /api/automation/workflows/{workflow_id}/agent-sdk/execute/
Body: {
  "task": "Fix the bug in data validation",
  "model": "sonnet",              // Optional: sonnet|opus|haiku
  "session_id": "uuid",           // Optional: for chat persistence
  "claude_session_id": "...",     // Optional: for resuming agent
  "attachment": {...}             // Optional: file attachment
}
Response: { "operation_id": "uuid", "status": "pending" } (HTTP 202)
```

### Check Operation Status
```
GET /api/automation/agent-sdk/operations/{operation_id}/status/
Response: {
  "operation_id": "uuid",
  "status": "pending|running|completed|failed|cancelled",
  "progress": 0-100,
  "progress_log": "Step-by-step log",
  "result": {...}
}
```

### Cancel Operation
```
POST /api/automation/agent-sdk/operations/{operation_id}/cancel/
```

### Build Workflow (Agent-Only Mode)
```
POST /api/automation/sessions/{session_id}/agent-sdk/build/
Body: {
  "request": "Extract invoices from Gmail and upload to Drive",
  "model": "sonnet"
}
Response: { "workflow_id": "uuid", "operation_id": "uuid", "status": "pending" }
```

### Status Check
```
GET /api/automation/agent-sdk/status/
Response: { "available": true, "version": "0.1.19" }
```

---

## 7. Database Models

### AsyncOperation (Line 2010 in models.py)

Tracks all async operations including agent executions.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUIDField | Primary key |
| `operation_type` | CharField | `'agent_execution'` for agent ops |
| `status` | CharField | `queued|pending|running|completed|failed|cancelled` |
| `progress_percentage` | IntegerField | 0-100 |
| `progress_log` | TextField | Step-by-step log |
| `current_step` | CharField | Current operation description |
| `queue_name` | CharField | `'agent_queue'` |
| `result_data` | JSONField | Final results |
| `error_message` | TextField | Error if failed |

### Related Models

| Model | Purpose |
|-------|---------|
| `Workflow` | Target of agent modifications |
| `Node` | Workflow steps (created/modified by agent) |
| `NodeVersion` | Node configuration versions |
| `CodeVersion` | Versioned code (created by agent) |
| `RecordingSession` | Tracks chat sessions, stores `claude_session_id` |

---

## 8. Worker Queue System

### 4 Queues

| Queue | Purpose | Concurrency |
|-------|---------|-------------|
| `build_queue` | Code generation, UI updates | 12 |
| `run_queue` | Workflow execution | 12 |
| `system_queue` | Background maintenance | 12 |
| `agent_queue` | Agent SDK operations | **3** (throttled) |

### Agent Queue Details

- Lower concurrency (3) because agent operations are expensive
- SQS long polling with adaptive intervals
- 30-second visibility timeout
- TIMEOUT_SECONDS = 1800 (30 minutes)

### Start Workers Locally

```bash
cd workers
docker-compose -f docker-compose.workers.yml \
               -f docker-compose.workers.local.yml \
               up -d --build
```

---

## 9. Session Persistence

### Two Session IDs

| ID | Purpose |
|----|---------|
| `session_id` (RecordingSession.id) | Links chat history, WebSocket targeting |
| `claude_session_id` | Resumes agent conversations, stored in `RecordingSession.claude_session_id` |

### Session Resume Flow

```
1. Initial execution:
   - AgentSDKService.execute_agent(workflow, task)
   - Returns messages including session_id
   - Store in RecordingSession.claude_session_id

2. Follow-up execution:
   - Call with claude_session_id=stored_value
   - Agent resumes context from previous conversation

3. If resume fails (container restart):
   - Clear invalid session_id
   - Retry without resume (fresh conversation)
   - Store new session_id
```

### Session Storage Location

Sessions stored in **Claude Code CLI process state** inside Docker containers:
- ✅ Survives: page refresh, multiple requests, 35+ min gaps
- ❌ Dies with: container restart, worker restart, deployment

**Solution options documented in:** `specs/47-session-management-ClaudeSDKCLient/47-08-FINAL-session-persistence-solutions.md`

---

## 10. Security & Resource Limits

### Allowed Tools (Whitelist)

Only MCP tools can be called:
```
mcp__bigbongo_workflow__get_workflow_context
mcp__bigbongo_workflow__list_nodes
mcp__bigbongo_workflow__check_workflow_credentials
mcp__bigbongo_workflow__get_node_code
mcp__bigbongo_workflow__update_node_code
mcp__bigbongo_workflow__get_node_schema
mcp__bigbongo_workflow__update_node_schema
mcp__bigbongo_workflow__execute_workflow_test
mcp__bigbongo_workflow__get_node_execution_data
mcp__bigbongo_workflow__modify_interface
mcp__bigbongo_workflow__modify_workflow_flow
mcp__bigbongo_workflow__create_workflow_nodes
mcp__bigbongo_workflow__modify_workflow_nodes
mcp__bigbongo_workflow__inspect_document_structure
```

### Blocked Tools (Blacklist)

```python
disallowed_tools = [
    'Write',         # File write
    'Edit',          # File edit
    'Read',          # File read
    'Glob',          # File search
    'Grep',          # Content search
    'Bash',          # Shell commands
    'NotebookEdit',  # Jupyter
]
```

### Resource Limits

```python
options_kwargs = {
    'max_turns': 20,         # Prevents infinite loops
    'max_budget_usd': 2.0,   # Cost cap per execution
    'permission_mode': 'acceptEdits',
    'model': 'sonnet',       # sonnet|opus|haiku
}
```

### Security Boundary

```
Agent CAN:
├─ Read/write node CODE (in database)
├─ Read/write node SCHEMAS (in database)
├─ Execute workflow tests
├─ Queue async operations
└─ Modify workflow flow

Agent CANNOT:
├─ Access filesystem
├─ Run shell commands
├─ Access other workflows (scoped to workflow_id)
├─ Access user data directly
└─ Make arbitrary network requests
```

---

## 11. WebSocket Real-Time Updates

### Connection

```
ws://localhost:8007/ws/recorder/sessions/{session_id}/
```

### Message Types

| Type | When Sent | Purpose |
|------|-----------|---------|
| `agent_sdk_activity` | Agent thinks/uses tools | Real-time activity updates |
| `agent_sdk_response` | Agent completes | Final response + activities |
| `execution_status_update` | Workflow test runs | Test progress |
| `code_regeneration_complete` | `update_node_code` | Refresh node code display |
| `diagram_update` | `update_node_schema` | Refresh workflow diagram |
| `interface_modified` | `modify_interface` | Reload interface preview |
| `nodes_created` | `create_workflow_nodes` | Refresh nodes list |

### Implementation Pattern

```python
if session_id:
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            f'session_{session_id}',
            {
                'type': 'event_name',
                'workflow_id': workflow_id,
                # ... event data
            }
        )
```

---

## 12. System Prompt Architecture

### Prompt Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                                 │
├─────────────────────────────────────────────────────────────────┤
│ 1. BigBongo System Context                                      │
│    - From: automation/prompts/bigbongo_context.md               │
│    - Explains BigBongo platform, BPMN, technical context        │
│                                                                 │
│ 2. Target Workflow                                              │
│    - Workflow ID, Name                                          │
│    - Original Request, Request Summary                          │
│                                                                 │
│ 3. Build Mode Instructions (optional)                           │
│    - Guidelines for creating workflow from scratch              │
│    - Node architecture (container vs action nodes)              │
│    - Exactly 2 LLM responses requirement                        │
│                                                                 │
│ 4. MCP Tools Documentation                                      │
│    - Detailed usage for each tool                               │
│    - Code pattern requirements                                  │
│    - Forbidden patterns                                         │
│    - Data flow conventions                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Instructions in Prompt

- **Parallel Tool Calls**: XML-tagged instruction for efficiency
- **Mandatory Testing**: Must run `execute_workflow_test` after changes
- **Credential Error Handling**: Don't try to "fix" auth issues in code
- **Tool Restrictions**: Explicit list of blocked tools

---

## 13. Code Patterns (Critical)

### CORRECT Patterns

**Function Signature - ALWAYS use this exact signature:**
```python
def execute(input_data, config=None):
    '''Docstring here'''
    # Your code
    return {"success": True, "data": {...}, "message": "Done"}
```

**Credential Access - ALWAYS use get_credential directly:**
```python
creds = get_credential('gmail')         # For Gmail
creds = get_credential('google-drive')  # For Google Drive
```

### FORBIDDEN Patterns

```python
# ❌ WRONG - Wrong function signature
def execute(context: dict, inputs: dict) -> dict:

# ❌ WRONG - Wrong credential function (underscore)
creds = _get_credential('gmail')

# ❌ WRONG - Credential from context
get_cred_func = context.get('_get_credential')
```

### Data Flow Convention

The executor automatically UNWRAPS data between nodes:
- Node 1 returns: `{"success": True, "data": {"message_id": "abc123"}, "message": "Found"}`
- Node 2 receives in `input_data`: `{"message_id": "abc123"}` (unwrapped!)

---

## 14. Testing & Debugging

### Quick Checks

```bash
# Check if Agent SDK is available
curl http://localhost:8006/api/automation/agent-sdk/status/

# Check operation status
curl http://localhost:8006/api/automation/agent-sdk/operations/{operation_id}/status/
```

### View Logs

```bash
# Django logs
tail -f _logs/debug.log | grep -i agent

# Worker logs
docker-compose -f docker-compose.workers.yml logs -f worker-agent
```

### Test Agent Manually (Django Shell)

```python
from automation.services.agent_sdk_service import AgentSDKService
from automation.models import Workflow

workflow = Workflow.objects.get(id="...")
async for msg in AgentSDKService.execute_agent(
    workflow,
    "list all nodes and their purposes"
):
    print(msg)
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Agent sees no nodes after add | Race condition | Use sync creation |
| Messages disappear on refresh | Not persisted | Check saveSystemMessage() |
| Agent loops forever | max_turns not working | Check options_kwargs |
| "Missing credentials" | Auth not connected | Direct user to /integrations/ |

### Run Tests

```bash
PYENV_VERSION=bigbongo-3-12-0 python manage.py test automation.tests.test_agent
```

---

## 15. Related Specifications

| Spec | Content |
|------|---------|
| `specs/47-session-management-ClaudeSDKCLient/` | Session persistence research & solutions |
| `specs/48-agents-sdk-pp/` | Full architecture documentation |
| `specs/53-lead-changes-summary/` | Recent changes & improvements |
| `specs/49-agent-only/` | Agent-only mode planning |
| `specs/50-chat-inconsistencies/` | Chat persistence fixes |
| `specs/52-nested-node-architecture/` | Nested node design decisions |

### Ticket Files (in specs/48-agents-sdk-pp/tickets/)

- `BB-259-agent-button-visibility.md`
- `BB-260-credential-notification-flow.md`
- `BB-261-duplicate-content.md`
- `BB-262-executions-realtime-update.md`
- `BB-263-step-visual-states.md`
- `BB-264-auto-skip-logic-critical.md`
- `BB-265-all-skipped-should-fail.md`
- `BB-266-agent-verification-after-build.md`
- `BB-267-investigate-build-inconsistency.md`
- `BB-268-required-integrations-population.md`

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...           # Claude API key
AWS_ACCESS_KEY_ID=...                  # AWS credentials
AWS_SECRET_ACCESS_KEY=...
AWS_SQS_REGION=us-east-1               # SQS region
```

---

## Quick Start for New Developers

1. **Read this file** - Understand the architecture
2. **Read the spec** for your Jira ticket (usually in `specs/48-agents-sdk-pp/tickets/`)
3. **Start local workers**: `docker-compose -f docker-compose.workers.yml -f docker-compose.workers.local.yml up -d --build`
4. **Tail logs**: `tail -f _logs/debug.log | grep -i agent`
5. **Key entry points**:
   - API: `api_views_agent_sdk.py:agent_sdk_execute()`
   - Service: `agent_sdk_service.py:execute_agent()`
   - MCP Tools: `agent_mcp_tools.py`
