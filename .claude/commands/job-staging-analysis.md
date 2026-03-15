---
name: job-staging-analysis
description: Full analysis of a workflow job on staging server
---

Analyze a workflow job on the staging server for debugging fix-it feature, BPMN loading, skip conditions, and execution issues.

Usage: `/job-staging-analysis <workflow_id> <session_id>`

Example: `/job-staging-analysis 85ec21d8-ef9e-4df8-b77f-6ed79bdf053e 097dce3b-4db7-442f-98d5-ce33221df65f`

## Configuration (Edit for your setup)

```
SSH_KEY=bigbongo_key
SSH_USER=demetrios
SSH_HOST=62.171.136.238
STAGING_PATH=/var/www/bigbongo-staging
PYTHON_PATH=/root/.pyenv/versions/bigbongo-staging-3-12-0/bin/python
```

**To use**: Replace the values above with your SSH key filename, username, etc.

## Analysis Steps

### 1. Connect to Staging

- SSH: `ssh -i $SSH_KEY $SSH_USER@$SSH_HOST`
- Staging path: `$STAGING_PATH`
- Python path: `sudo $PYTHON_PATH`

### 2. Check Workflow Execution

Run Django shell on staging to get execution details. Note: Use `sudo` with full python path since demetrios user can't access root's pyenv directly.

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd $STAGING_PATH && sudo $PYTHON_PATH manage.py shell -c \"
from automation.models import WorkflowExecution, WorkflowVersion, Workflow
# First try to find by workflow_id directly
workflow = Workflow.objects.filter(id='<workflow_id>').first()
if workflow:
    print('Workflow:', workflow.name)
    print('Workflow ID:', workflow.id)
    # Get latest execution
    exec_obj = WorkflowExecution.objects.filter(workflow=workflow).order_by('-started_at').first()
    if exec_obj:
        print('Execution ID:', exec_obj.id)
        print('Celery Task ID:', exec_obj.celery_task_id)
        print('Status:', exec_obj.status)
        print('Error:', exec_obj.error_message)
        # Check BPMN version
        version = WorkflowVersion.objects.filter(workflow=workflow).order_by('-created_at').first()
        if version:
            print('Version:', version.version_number)
            bpmn = version.bpmn_json or {}
            steps = bpmn.get('steps', [])
            print('BPMN Steps:', len(steps))
            for s in steps:
                skip = s.get('skip_conditions')
                if skip:
                    print('  Skip:', s.get('name'), skip)
    else:
        print('No executions found for this workflow')
else:
    # Try finding by celery_task_id
    exec_obj = WorkflowExecution.objects.filter(celery_task_id='<workflow_id>').first()
    if exec_obj:
        print('Found by celery_task_id')
        print('Workflow:', exec_obj.workflow.name)
        print('Status:', exec_obj.status)
        print('Error:', exec_obj.error_message)
    else:
        print('No workflow or execution found with ID:', '<workflow_id>')
        # Show recent executions for reference
        recent = WorkflowExecution.objects.order_by('-started_at')[:5]
        print('Recent executions:')
        for e in recent:
            print('  -', e.id, '|', e.celery_task_id, '|', e.status, '|', e.workflow.name if e.workflow else 'N/A')
\""
```

### 3. Check Debug Logs for Workflow Execution

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "grep -E '(<workflow_id>|<session_id>)' $STAGING_PATH/_logs/debug.log | tail -100"
```

### 4. Check Debug Logs for BPMN Loading & Skip Checks

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "grep -E '(<workflow_id>|BPMN_LOAD|SKIP_CHECK)' $STAGING_PATH/_logs/debug.log | tail -100"
```

### 5. Check for Fix-It Actions (modify_workflow_flow)

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "grep -E '(<session_id>|modify_workflow_flow|flow_modification_complete|skip_bpmn)' $STAGING_PATH/_logs/debug.log | tail -100"
```

### 6. Check Error Classification

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "grep -E '(<session_id>|error_classification|classify_error|ErrorType)' $STAGING_PATH/_logs/debug.log | tail -50"
```

### 7. Check Node Runs

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd $STAGING_PATH && sudo $PYTHON_PATH manage.py shell -c \"
from automation.models import WorkflowExecution, NodeRun
exec_obj = WorkflowExecution.objects.filter(workflow_id='<workflow_id>').order_by('-started_at').first()
if exec_obj:
    runs = NodeRun.objects.filter(workflow_execution=exec_obj).order_by('started_at')
    for r in runs:
        print(r.node.name if r.node else '-', '|', r.status, '|', r.error_message[:50] if r.error_message else '-')
\""
```

## Summary Report Format

After running the analysis, provide a summary:

| Category          | Finding                 |
| ----------------- | ----------------------- |
| Workflow          | Name and ID             |
| Execution Status  | Success/Failed/Running  |
| Failed Node       | Node name if applicable |
| Error Type        | CODE/FLOW/INTERFACE     |
| BPMN Loaded       | Yes/No                  |
| Skip Conditions   | List any found          |
| Fix Actions Taken | List modifications made |
| Root Cause        | Brief explanation       |
| Recommendation    | Next steps              |
