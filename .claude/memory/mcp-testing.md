# MCP Testing & Workflow Creation

**IMPORTANT**: When adding new MCP testing tools, always update this file with the tool documentation.

## Test User Login Credentials

**See**: `.claude/memory/mcp-testing-credentials.local.md` for login credentials (gitignored)

- **Login URL**: `/accounts/login/`
- **Login form selector**: `input[type="email"]` (NOT `input[name="login"]`)

## Creating Workflows via Browser (Playwright Testing)

**IMPORTANT**: Workflows are created through the CHAT interface, not through modal forms on the Jobs page.

### Steps to create a new workflow:
1. Navigate to `/jobs/new/` (or hover on "I have something in mind" card on home page, then click "Chat")
2. This creates a draft workflow and redirects to chat interface at `/jobs/draft/{uuid}/`
3. Type your workflow request in the chat textarea
4. Press Enter to submit
5. The agent will process and create the workflow nodes

### URL patterns:
- New chat: `/jobs/new/`
- Draft workflow chat: `/jobs/draft/{workflow_uuid}/{session_uuid}/`
- Published workflow: `/jobs/{workflow_uuid}/{session_uuid}/`
- Jobs list: `/jobs/`

### Hover behavior on home page:
- The "I have something in mind" card requires HOVER to reveal "Continue with voice" and "Chat" buttons
- The Chat button is an `<a>` tag linking to `{% url 'automation:new_chat' %}` which maps to `/jobs/new/`

## Available MCP Testing Tools

### Browser Control

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__login` | Login to BigBongo | `username`, `password`, `base_url` |
| `mcp__bigbongo-testing__navigate` | Navigate to URL | `url` |
| `mcp__bigbongo-testing__click` | Click element | `selector` or `text` |
| `mcp__bigbongo-testing__hover` | Hover over element | `selector` or `text` |
| `mcp__bigbongo-testing__double_click` | Double-click element | `selector` or `text` |
| `mcp__bigbongo-testing__right_click` | Right-click element | `selector` or `text` |
| `mcp__bigbongo-testing__drag_and_drop` | Drag from one element to another | `from_selector`, `to_selector` |
| `mcp__bigbongo-testing__focus` | Focus an element | `selector` |
| `mcp__bigbongo-testing__fill` | Fill input field | `selector`, `value` |
| `mcp__bigbongo-testing__type_text` | Type with keystrokes (triggers events) | `selector`, `value` |
| `mcp__bigbongo-testing__press_key` | Press keyboard key | `key` (Enter, Tab, Escape, etc.) |
| `mcp__bigbongo-testing__screenshot` | Take screenshot | `name` (optional) |
| `mcp__bigbongo-testing__scroll` | Scroll page | `direction` (up/down), `amount` |
| `mcp__bigbongo-testing__wait_for_selector` | Wait for element | `selector`, `timeout` |
| `mcp__bigbongo-testing__select_option` | Select dropdown option | `selector`, `value` or `label` |
| `mcp__bigbongo-testing__get_element_text` | Get element text content | `selector` |
| `mcp__bigbongo-testing__close_browser` | Close browser and cleanup | - |

### Page Context & Filtering

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__get_page_content` | Get HTML, URL, title, console logs, network | - |
| `mcp__bigbongo-testing__get_full_context` | Browser + DB + WebSocket state | `session_id` (optional) |
| `mcp__bigbongo-testing__get_visible_text` | Get text content only (lighter than get_page_content) | `selector` (default: body) |
| `mcp__bigbongo-testing__query_selector_all` | Query elements and get attributes | `selector`, `attributes` |

### Browser State Persistence

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__save_browser_state` | Save cookies/localStorage for later | `name` |
| `mcp__bigbongo-testing__restore_browser_state` | Restore saved state (skip re-login) | `name` |
| `mcp__bigbongo-testing__get_cookies` | Get all browser cookies | - |

### Network Request Waiting

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__wait_for_request` | Wait for request matching URL pattern | `url_pattern`, `method`, `timeout` |
| `mcp__bigbongo-testing__wait_for_response` | Wait for response and get body | `url_pattern`, `timeout` |

### Assertions (Test Verification)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__assert_element_exists` | Assert element exists on page | `selector`, `timeout` |
| `mcp__bigbongo-testing__assert_text_contains` | Assert element text contains string | `selector`, `text`, `timeout` |
| `mcp__bigbongo-testing__assert_url_contains` | Assert current URL contains string | `text` |
| `mcp__bigbongo-testing__assert_workflow_succeeded` | Assert workflow execution succeeded | `execution_id` |
| `mcp__bigbongo-testing__assert_node_output_contains` | Assert node output has key/value | `execution_id`, `node_id`, `key`, `expected_value` |

### Form & Table Helpers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__fill_form` | Fill multiple form fields at once | `fields` (dict), `submit`, `submit_selector` |
| `mcp__bigbongo-testing__get_table_data` | Extract table as list of dicts | `selector`, `headers`, `max_rows` |
| `mcp__bigbongo-testing__retry_until` | Retry action until success | `action`, `params`, `max_retries`, `delay` |

### Database Queries

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__query_db` | Query database records | `model` (async_operation, workflow, nodes, recording_session), `filters` |
| `mcp__bigbongo-testing__get_workflow_details` | Full workflow info with nodes and integrations | `workflow_id`, `user_id` (optional) |
| `mcp__bigbongo-testing__get_node_details` | Node code, schema, purpose | `node_id` |
| `mcp__bigbongo-testing__get_code_versions` | Node code version history | `node_id`, `limit` |
| `mcp__bigbongo-testing__get_available_integrations` | List integrations and credentials | `user_id` (optional), `include_credentials` |

### Workflow Execution

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__execute_workflow` | Run workflow synchronously | `workflow_id`, `input_data` |
| `mcp__bigbongo-testing__run_node_test` | Test single node | `node_id`, `input_data` |
| `mcp__bigbongo-testing__get_workflow_executions` | Get execution history | `workflow_id`, `limit` |
| `mcp__bigbongo-testing__get_workflow_execution` | Get execution details with node results | `execution_id` |

### Async Operations & Waiting

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__wait_for_operation` | Poll until operation completes | `operation_id`, `timeout`, `poll_interval` |
| `mcp__bigbongo-testing__wait_for_workflow_ready` | Wait for workflow nodes to have code | `workflow_id`, `timeout`, `poll_interval` |

### Agent/Chat Testing

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__create_test_user` | Create or get test user | `username`, `email`, `password` |
| `mcp__bigbongo-testing__create_session` | Create recording session | `workflow_id`, `user_id`, `name` |
| `mcp__bigbongo-testing__send_agent_message` | Send message to agent | `workflow_id`, `session_id`, `message`, `model` |
| `mcp__bigbongo-testing__wait_for_agent_response` | Wait for agent reply | `session_id`, `timeout`, `last_message_count` |
| `mcp__bigbongo-testing__send_agent_message_and_wait` | Send message AND wait for reply (combined) | `workflow_id`, `session_id`, `message`, `timeout` |
| `mcp__bigbongo-testing__get_session_details` | Get session with chat transcript | `session_id` |

### WebSocket Monitoring

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__connect_websocket` | Connect to session WebSocket (unauthenticated) | `session_id`, `base_url` |
| `mcp__bigbongo-testing__connect_websocket_authenticated` | Connect with browser cookies (for auth) | `session_id`, `base_url`, `cookies` |
| `mcp__bigbongo-testing__get_ws_events` | Get captured WebSocket events | `session_id`, `event_type` (optional) |

### Integration Testing

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp__bigbongo-testing__list_integrations` | List all integrations with analysis status | `include_unanalyzed` (bool) |
| `mcp__bigbongo-testing__get_integration_details` | Get integration details with auth methods & versions | `integration_id` |
| `mcp__bigbongo-testing__trigger_integration_analysis` | Trigger AI analysis for an integration | `integration_id` |
| `mcp__bigbongo-testing__wait_for_integration_analysis` | Wait for analysis to complete | `integration_id`, `timeout`, `poll_interval` |
| `mcp__bigbongo-testing__get_auth_method_versions` | Get config versions for an auth method | `auth_method_id` |
| `mcp__bigbongo-testing__activate_config_version` | Activate a specific config version | `version_id` |
| `mcp__bigbongo-testing__send_integration_chat` | Send message to integration chat agent | `integration_id`, `message`, `timeout` |

## Standard Test Flow

### 1. Login (or Restore Saved State)

```python
# Option A: Fresh login
mcp__bigbongo-testing__login(username="test@bigbongo.ai", password="TestPass123!")
mcp__bigbongo-testing__save_browser_state(name="logged-in")  # Save for reuse

# Option B: Restore saved session (faster)
mcp__bigbongo-testing__restore_browser_state(name="logged-in")
```

### 2. Create Workflow via Chat

```python
mcp__bigbongo-testing__navigate(url="http://localhost:8006/jobs/new/")
mcp__bigbongo-testing__wait_for_selector(selector="textarea")
mcp__bigbongo-testing__type_text(selector="textarea", value="<workflow request>")
mcp__bigbongo-testing__press_key(key="Enter")

# NEW: Wait for workflow to be ready (no more hardcoded sleeps!)
mcp__bigbongo-testing__assert_url_contains(text="/jobs/")  # Verify redirect
# Extract workflow_id from URL, then:
mcp__bigbongo-testing__wait_for_workflow_ready(workflow_id="<uuid>", timeout=60)
```

### 3. Verify Workflow Structure

```python
mcp__bigbongo-testing__get_workflow_details(workflow_id="<uuid>", user_id=5)
# Use lighter alternatives to get_page_content:
mcp__bigbongo-testing__get_visible_text(selector="#nodes-panel")
mcp__bigbongo-testing__query_selector_all(selector=".node-card", attributes=["innerText", "data-node-id"])
```

### 4. Execute and Verify with Assertions

```python
result = mcp__bigbongo-testing__execute_workflow(workflow_id="<uuid>", input_data={})
execution_id = result["execution_id"]

# NEW: Use assertions for verification
mcp__bigbongo-testing__assert_workflow_succeeded(execution_id=execution_id)
mcp__bigbongo-testing__assert_node_output_contains(
    execution_id=execution_id,
    node_id="<node_id>",
    key="success",
    expected_value=True
)
mcp__bigbongo-testing__screenshot(name="test-complete")
```

### 5. WebSocket Monitoring (Authenticated)

```python
# Get cookies from browser for authenticated WebSocket connection
cookies = mcp__bigbongo-testing__get_cookies()
mcp__bigbongo-testing__connect_websocket_authenticated(
    session_id="<session_uuid>",
    cookies=cookies["cookies"]
)
# Later: mcp__bigbongo-testing__get_ws_events(session_id="<session_uuid>")
```

## Integration Testing Checklist

- [ ] Workflow created successfully with expected nodes
- [ ] Correct integrations detected and used
- [ ] Credential calls use canonical service IDs (e.g., 'google-gmail' not 'gmail')
- [ ] Workflow executes without errors
- [ ] Output data matches expected format/content
- [ ] Screenshot captured for visual verification

## Form, Table & Retry Examples

### Fill Form (multiple fields at once)

```python
mcp__bigbongo-testing__fill_form(
    fields={
        "#name": "John Doe",
        "#email": "john@example.com",
        "#country": {"value": "US", "type": "select"},
        "#terms": {"value": True, "type": "checkbox"}
    },
    submit=True,
    submit_selector="button[type='submit']"
)
```

### Extract Table Data

```python
# Auto-detects headers from thead
result = mcp__bigbongo-testing__get_table_data(selector="table.workflows")
# Returns: {headers: ["Name", "Status", "Created"], data: [{Name: "...", Status: "...", ...}]}

# With custom headers
result = mcp__bigbongo-testing__get_table_data(
    selector="table",
    headers=["ID", "Name", "Value"],
    max_rows=50
)
```

### Retry Flaky Operations

```python
# Retry element assertion up to 5 times with 2s delay
mcp__bigbongo-testing__retry_until(
    action="assert_element_exists",
    params={"selector": ".loading-complete", "timeout": 2000},
    max_retries=5,
    delay=2.0
)

# Retry click that might fail due to animation
mcp__bigbongo-testing__retry_until(
    action="click",
    params={"selector": ".dropdown-item"},
    max_retries=3,
    delay=0.5
)
