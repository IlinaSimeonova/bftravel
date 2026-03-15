---
name: save-test-case
description: |
  Save a workflow as a test case for MCP testing.
  Extracts workflow details and latest execution inputs from a job URL,
  then appends it to mcp-test-cases.local.md for future testing.
args: "<job_url> - URL like http://localhost:8006/jobs/{workflow_id}/{session_id}/"
---

# Save Workflow as Test Case

This skill captures a workflow's configuration and execution inputs so it can be replicated in automated tests.

## URL Format

The job URL format is: `http://localhost:8006/jobs/{workflow_id}/{session_id}/`

Example: `http://localhost:8006/jobs/5a78f8b9-c8d4-4273-ac28-2dfcfbdebf55/a67f18f0-4d55-4740-aae6-ee14c39aa904/`

## Execution Steps

### 1. Parse the URL

Extract `workflow_id` from the URL path. The format is `/jobs/{workflow_id}/{session_id}/`.

### 2. Get Workflow Details

Use the MCP testing tools to get workflow information:

```
mcp__bigbongo-testing__get_workflow_details(workflow_id="<uuid>", user_id=5)
```

This returns:
- `name` - Workflow name (usually the original request)
- `nodes` - List of nodes with names and types
- `last_execution` - Latest execution info

### 3. Get Latest Execution Input Data

If `last_execution` exists, get the full execution details:

```
mcp__bigbongo-testing__get_workflow_execution(execution_id="<uuid>")
```

This returns:
- `execution_context.initial_input` - The input data used
- `node_runs` - Each node's input/output data

### 4. Get Original Request

Query the workflow to get the original request that created it:

```
mcp__bigbongo-testing__query_db(model="workflow", filters={"workflow_id": "<uuid>"})
```

Or use the workflow name which typically contains the original request.

### 5. Append to Test Cases File

Read the current `.claude/memory/mcp-test-cases.local.md` file and append a new test case in this format:

```markdown
---

## Test N: [Descriptive Name]

**Purpose**: [What this test verifies]

**Workflow prompt**:
```
[Original request that created the workflow]
```

**Workflow ID**: `[uuid]` (for re-running existing workflow)

**Test inputs**:
```json
{
  "key": "value"
}
```

**Expected**:
- [Number] nodes created: [Node names]
- [Integration requirements]
- [Expected outputs]

**Verification**:
```python
mcp__bigbongo-testing__execute_workflow(
    workflow_id="[uuid]",
    input_data={...}
)
```
```

### 6. Confirm Success

Report what was saved:
- Workflow name
- Number of nodes
- Input parameters captured
- File updated

## Example Output

After running `/save-test-case http://localhost:8006/jobs/5a78f8b9.../a67f18f0.../`:

```
Saved test case to mcp-test-cases.local.md:
- Workflow: "Read Google Doc and summarize"
- Nodes: 2 (Read Google Doc, Create Summary)
- Inputs: {"document_url": "https://docs.google.com/..."}
```

## Notes

- The test case file is `.local.md` so it's gitignored (may contain sensitive URLs)
- If workflow has no executions yet, inputs will be empty
- The skill determines the next test number automatically by counting existing tests
