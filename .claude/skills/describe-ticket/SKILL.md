# Describe Ticket Skill

Update a Jira ticket description with structured technical analysis.

## Usage
```
/describe-ticket <ISSUE-KEY>
```

Example: `/describe-ticket BB-277`

## What This Skill Does

1. Gets the current ticket info from Jira
2. Analyzes the issue based on conversation context or prompts for details
3. Updates the ticket description with a well-formatted technical analysis

## Description Template

Use this EXACT format when updating the description. Use standard Markdown (NOT Jira wiki markup):

```
## Problem
[1-2 sentence description of what's broken/needed]

## Root Cause
[Technical explanation of WHY this happens]

## Bug Origin
- `filename.py` - [what it does wrong]
- `another_file.js` - [what it does wrong]

## Proposed Solution
1. [Step 1 of the fix]
2. [Step 2 of the fix]
3. [Step 3 if needed]

## Files to Modify
- `filename1` - [what change]
- `filename2` - [what change]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
```

## Instructions

1. First, fetch the ticket using `getJiraIssue` to see current state
2. If you don't have enough context, ask the user for:
   - What is the problem?
   - What should happen instead?
   - Any error messages or logs?
3. Analyze the codebase if needed to find root cause
4. Format the description using the template above
5. Update using `editJiraIssue` with markdown string

## Important Formatting Rules

- Use `##` for headings (standard Markdown H2)
- Use `-` for bullet points (NOT `*`)
- Use `1. 2. 3.` for numbered lists (NOT `#`)
- Use backticks for inline code: \`filename.py\` (NOT double braces)
- Keep each section SHORT and PRECISE (2-3 lines max)
- No emojis in the description
- **NO CODE BLOCKS** - Never include actual code snippets, only reference filenames and function names
- Focus on WHAT and WHY, not HOW (code details belong in PR, not ticket)
- **NEVER use Jira wiki markup** like `h2.`, `{{code}}`, or `#` for lists - use standard Markdown only

## Example Output

```
## Problem
Interface panel shows stale data when agent runs execute_workflow_test - no test inputs, no running state, no results displayed.

## Root Cause
Interface is an iframe with isolated JS context. WebSocket events go to parent window which updates steps panel but never forwards to iframe.

## Bug Origin
- `workflow_chat.html` - WebSocket handler receives execution_status_update
- Updates right panel (nodes status) but has no code to notify iframe

## Proposed Solution
1. Add test_inputs to WebSocket event payload from execute_workflow_test
2. Add postMessage sender in parent to forward events to iframe
3. Add message listener in iframe to receive and display test data

## Files to Modify
- `agent_mcp_tools.py` - Include is_agent_test and test_inputs in WebSocket events
- `workflow_chat.html` - Add notifyInterfaceAgentTest() function
- `workflow-interface.js` - Add message listener and input population

## Acceptance Criteria
- [ ] Interface shows test input values when agent runs test
- [ ] Interface shows running state during agent test
- [ ] Interface displays results when test completes
```
