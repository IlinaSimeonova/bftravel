---
name: mcp-test
description: |
  Run E2E tests using MCP testing tools against BigBongo workflows.
  Creates workflows via browser, tests integrations, and verifies agent behavior.
  Accepts a prompt describing what to test.
args: "<test prompt> - describe what workflow/integration to test"
---

# MCP Workflow Testing

This skill uses MCP testing tools to perform end-to-end tests of BigBongo workflows.

## Reference Documentation

**IMPORTANT**: Before testing, read the MCP testing documentation:
- `.claude/memory/mcp-testing.md` - Login credentials, URL patterns, workflow creation steps

## Test User Credentials

**See**: `.claude/memory/mcp-testing-credentials.local.md` for login credentials (gitignored)

## Available MCP Tools

### Browser Control
- `mcp__bigbongo-testing__login` - Login to BigBongo
- `mcp__bigbongo-testing__navigate` - Navigate to URL
- `mcp__bigbongo-testing__click` - Click element by selector or text
- `mcp__bigbongo-testing__hover` - Hover over element
- `mcp__bigbongo-testing__fill` - Fill input field
- `mcp__bigbongo-testing__type_text` - Type with keystrokes (triggers events)
- `mcp__bigbongo-testing__press_key` - Press keyboard key (Enter, Tab, etc.)
- `mcp__bigbongo-testing__screenshot` - Take screenshot
- `mcp__bigbongo-testing__scroll` - Scroll page
- `mcp__bigbongo-testing__wait_for_selector` - Wait for element

### Data Access
- `mcp__bigbongo-testing__query_db` - Query workflows, nodes, operations
- `mcp__bigbongo-testing__get_workflow_details` - Get full workflow info
- `mcp__bigbongo-testing__get_node_details` - Get node code and schema
- `mcp__bigbongo-testing__get_available_integrations` - List available integrations

### Workflow Execution
- `mcp__bigbongo-testing__execute_workflow` - Run workflow programmatically
- `mcp__bigbongo-testing__run_node_test` - Test single node

### Agent Testing
- `mcp__bigbongo-testing__create_session` - Create recording session
- `mcp__bigbongo-testing__send_agent_message` - Send message to agent
- `mcp__bigbongo-testing__wait_for_agent_response` - Wait for agent reply
- `mcp__bigbongo-testing__get_session_details` - Get chat transcript

### Context
- `mcp__bigbongo-testing__get_page_content` - Get HTML, console logs, network
- `mcp__bigbongo-testing__get_full_context` - Browser + DB + WebSocket state

## Standard Test Flow

### 1. Login and Navigate to New Chat

```
1. mcp__bigbongo-testing__login(username="test@bigbongo.ai", password="TestPass123!")
2. mcp__bigbongo-testing__navigate(url="http://localhost:8006/jobs/new/")
3. mcp__bigbongo-testing__wait_for_selector(selector="textarea")
```

### 2. Create Workflow via Chat

```
1. mcp__bigbongo-testing__type_text(selector="textarea", value="<workflow request>")
2. mcp__bigbongo-testing__press_key(key="Enter")
3. Wait for workflow creation (check page content for nodes panel)
```

### 3. Verify Workflow Structure

```
1. mcp__bigbongo-testing__get_page_content() - Check for nodes
2. mcp__bigbongo-testing__query_db(model="workflow", filters={"user_id": 5, "limit": 1})
3. mcp__bigbongo-testing__get_workflow_details(workflow_id="<uuid>")
```

### 4. Execute and Verify

```
1. mcp__bigbongo-testing__execute_workflow(workflow_id="<uuid>", input_data={})
2. Check execution results for success/failure
3. mcp__bigbongo-testing__screenshot() - Capture final state
```

## Integration Testing Examples

### Gmail Integration
```
Test prompt: "Download the latest email from Gmail"
Expected: Workflow with node using get_credential('google-gmail')
```

### Google Drive Integration
```
Test prompt: "Upload a file to Google Drive and get download link"
Expected: Workflow with node using get_credential('google-drive'), permission creation
```

### Multi-Integration
```
Test prompt: "Download invoice from Gmail and upload to Google Drive"
Expected: Multiple nodes with proper credential calls, base64 encoding for binary data
```

## Verification Checklist

After test execution:
- [ ] Workflow created successfully
- [ ] Correct integrations detected and used
- [ ] Credential calls use canonical service IDs (e.g., 'google-gmail' not 'gmail')
- [ ] Binary data properly base64 encoded between nodes
- [ ] Google Drive files have public permissions if sharing links
- [ ] No errors in execution output
- [ ] Screenshot captured for visual verification

## Error Handling

If tests fail:
1. Check `mcp__bigbongo-testing__get_page_content()` for console errors
2. Check network requests for API failures
3. Query `async_operation` model for operation status
4. Check Docker worker logs if background jobs fail

## Cleanup

After testing:
```
mcp__bigbongo-testing__close_browser()
```
