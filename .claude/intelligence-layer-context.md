# Intelligence Layer Developer Context

**Purpose:** Shared context for all developers working on Intelligence Layer tasks.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Data Models](#3-data-models)
4. [Core Files Reference](#4-core-files-reference)
5. [Interview System](#5-interview-system)
6. [Post-Interview Hooks](#6-post-interview-hooks)
7. [Automation Opportunities](#7-automation-opportunities)
8. [Synthetic Employees](#8-synthetic-employees)
9. [Invitation System](#9-invitation-system)
10. [WebSocket Real-Time Updates](#10-websocket-real-time-updates)
11. [API Endpoints](#11-api-endpoints)
12. [URL Routes](#12-url-routes)
13. [Prompts](#13-prompts)
14. [Related Specifications](#14-related-specifications)

---

## 1. Overview

The **Intelligence Layer** is BigBongo's employee interview and automation discovery system. It conducts AI-powered interviews with employees to understand their workflows, identify pain points, and discover automation opportunities.

### What the Intelligence Layer Does

- **Manages Companies & Employees** - Organization hierarchy with teams
- **Conducts AI Interviews** - Mapping interviews (broad) and deep-dive interviews (specific processes)
- **Analyzes Interview Data** - Post-interview hooks extract insights
- **Identifies Automation Opportunities** - Agent-ready specs for workflows
- **Supports Synthetic Employees** - AI-generated personas for testing/demos

### Key User Flows

```
1. COMPANY SETUP
   Staff creates Company → Invitation sent to Admin → Admin sets password → Admin can invite employees

2. EMPLOYEE INTERVIEW
   Admin invites Employee → Employee accepts → Employee does Mapping Interview →
   Hooks analyze → Deep-dive interviews queued → Employee continues until queue empty

3. AUTOMATION DISCOVERY
   All interviews analyzed → Automation opportunities identified →
   Admin reviews opportunities → Can build workflows with Agent SDK
```

---

## 2. Architecture

### Entity Hierarchy

```
Organization (Company)
├── Admin (User)
├── OrgUnits (Teams/Departments - self-referential hierarchy)
│   └── Children OrgUnits
└── OrganizationMembership (members)
    ├── SyntheticPersona (OneToOne, for synthetic members only)
    ├── InterviewSessions
    │   ├── InterviewMessages
    │   └── InterviewHookResults
    ├── InterviewQueueItems (pending interviews)
    ├── EmployeeAutomationAnalysis
    │   └── AutomationOpportunities
    └── EmployeeProfile (AI-built profile from interviews)
OrgUnit
└── TeamSynthesis (L2 cross-person synthesis, multiple per team)
```

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPANY DASHBOARD                            │
│   Admin sees: employees, interview progress, opportunities       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EMPLOYEE INTERVIEW                           │
│   Employee chats with AI → Messages stored → Session tracked    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (on session end)
┌─────────────────────────────────────────────────────────────────┐
│                   POST-INTERVIEW HOOKS                           │
│   Analyzers: summary, future_interviews, tool_extraction, etc.  │
│   Actions: queue_next_interviews, update_automation_opportunities│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AUTOMATION OPPORTUNITIES                        │
│   Employee-level cumulative analysis → Agent-ready specs        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Models

### 3.1 Company

Top-level organization container.

```python
class Company(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(User, null=True)  # null if pending invitation
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3.2 OrgUnit (Organization Unit)

Self-referential hierarchy for teams/departments.

```python
class OrgUnit(models.Model):
    id = models.UUIDField(primary_key=True)
    company = models.ForeignKey(Company)
    parent = models.ForeignKey('self', null=True)  # For nesting
    name = models.CharField(max_length=200)
    unit_type = models.CharField(choices=[
        ('department', 'Department'),
        ('team', 'Team'),
        ('group', 'Group'),
        ('division', 'Division'),
        ('other', 'Other'),
    ], default='team')
```

### 3.3 OrganizationMembership (replaces Employee)

Person in the organization (real or synthetic). Defined in `core/models.py`.

```python
class OrganizationMembership(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey(Organization, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    units = models.ManyToManyField(OrgUnit, blank=True)

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    job_title = models.CharField(blank=True)
    annual_salary = models.DecimalField(null=True)

    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_synthetic = models.BooleanField(default=False)
    slug = models.SlugField()
```

**Key Methods:**
- `get_interview_progress()` - Returns progress dict with percentage, completed/pending counts
- `get_hourly_rate()` - Calculates from annual_salary (for ROI)

### 3.3b SyntheticPersona

Persona details for synthetic members. OneToOne to OrganizationMembership.

```python
class SyntheticPersona(models.Model):
    membership = models.OneToOneField(OrganizationMembership, related_name='synthetic_persona')
    resistance_level = models.IntegerField(null=True)  # 1-10 scale
    archetype_key = models.CharField(blank=True)
    # Personal details: country_city, nationality, sex, date_of_birth, marital_status, children_count
    # Professional: education_level, field_of_study
    # Narrative: background, current_situation, motivation, triggering_event,
    #            frustrations_challenges, goals, tools_tried, actual_outcome
    # Profile: full_profile_md, profile_generated_at, profile_generation_model
```

### 3.4 InterviewSession

Single interview conversation.

```python
class InterviewSession(models.Model):
    id = models.UUIDField(primary_key=True)
    membership = models.ForeignKey(OrganizationMembership, related_name='interview_sessions')

    status = models.CharField(choices=['active', 'paused', 'completed'])
    interview_type = models.CharField(choices=['mapping', 'deep_dive'])
    is_synthetic = models.BooleanField(default=False)  # AI-generated interview

    topic = models.CharField(blank=True)  # From queue item
    summary = models.TextField(blank=True)  # Generated by hook

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
```

### 3.5 InterviewMessage

Individual chat messages.

```python
class InterviewMessage(models.Model):
    id = models.UUIDField(primary_key=True)
    session = models.ForeignKey(InterviewSession, related_name='messages')

    role = models.CharField(choices=['user', 'assistant', 'system'])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachments = models.JSONField(default=list)  # R2 URLs
```

### 3.6 InterviewHook

Registry of post-interview analysis hooks.

```python
class InterviewHook(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(unique=True)  # e.g., "summary"
    hook_type = models.CharField(choices=['analyzer', 'action'])
    display_name = models.CharField()
    prompt_file = models.CharField()  # e.g., "post-interview/analyzers/summary.md"

    enabled = models.BooleanField(default=True)
    applies_to = models.JSONField(default=list)  # ["mapping", "deep_dive"] or []
    requires_result_from = models.CharField(blank=True)  # Dependency
```

### 3.7 InterviewHookResult

Output from running a hook on a session.

```python
class InterviewHookResult(models.Model):
    id = models.UUIDField(primary_key=True)
    session = models.ForeignKey(InterviewSession, related_name='hook_results')
    hook = models.ForeignKey(InterviewHook)

    status = models.CharField(choices=[
        'pending', 'waiting', 'running', 'completed', 'failed', 'skipped'
    ])
    result_data = models.JSONField(default=dict)  # Structured output
    result_text = models.TextField(blank=True)  # Human-readable
    action_taken = models.TextField(blank=True)  # For action hooks
```

### 3.8 InterviewQueueItem

Pending interviews for a membership.

```python
class InterviewQueueItem(models.Model):
    id = models.UUIDField(primary_key=True)
    membership = models.ForeignKey(OrganizationMembership, related_name='interview_queue')

    interview_type = models.CharField(choices=['mapping', 'deep_dive'])
    is_continuation = models.BooleanField(default=False)
    topic = models.CharField(blank=True)
    priority = models.CharField(choices=['high', 'medium', 'low'])
    reason = models.TextField(blank=True)
    continuation_context = models.TextField(blank=True)  # Injected into greeting

    status = models.CharField(choices=['pending', 'in_progress', 'completed', 'skipped'])
    source_session = models.ForeignKey(InterviewSession, null=True)
```

### 3.9 EmployeeAutomationAnalysis

Cumulative automation analysis per membership.

```python
class EmployeeAutomationAnalysis(models.Model):
    id = models.UUIDField(primary_key=True)
    membership = models.OneToOneField(OrganizationMembership, related_name='automation_analysis')

    last_analyzed_at = models.DateTimeField(null=True)
    interviews_analyzed_count = models.IntegerField(default=0)
    interviews_analyzed_ids = models.JSONField(default=list)
    conflicts_report = models.JSONField(default=list)
```

### 3.10 AutomationOpportunity

Individual automation opportunity identified.

```python
class AutomationOpportunity(models.Model):
    id = models.UUIDField(primary_key=True)
    analysis = models.ForeignKey(EmployeeAutomationAnalysis, related_name='opportunities')

    # Content
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=500)
    human_readable_details = models.TextField()  # Bullet points
    full_spec_md = models.TextField()  # Agent-ready specification

    # Integrations
    raw_integration_names = models.JSONField(default=list)
    matched_service_ids = models.JSONField(default=list)

    # Scores
    time_per_run = models.CharField()  # '1min', '5min', '15min', '30min', '1hr', '2hr', '4hr', '8hr'
    time_saved = models.CharField()    # 'minimal', 'low', 'medium', 'high', 'very_high'
    complexity = models.CharField()    # 'easy', 'medium', 'hard'
    frequency = models.CharField()     # 'daily', 'weekly', 'monthly', 'occasional'
    confidence = models.CharField()    # 'high', 'medium', 'low'
    priority = models.CharField()      # 'high', 'medium', 'low'

    status = models.CharField(choices=['identified', 'built', 'deprecated'])
    opportunity_type = models.CharField(choices=['automation', 'process_improvement'])
```

### 3.11 TeamSynthesis

L2 cross-person synthesis for one OrgUnit. Multiple rows per team (re-runs create history).

```python
class TeamSynthesis(models.Model):
    id = UUIDField(primary_key=True)
    org_unit = ForeignKey('core.OrgUnit', related_name='team_syntheses')
    status = CharField(choices=['pending', 'running', 'completed', 'failed'])
    error_message = TextField(blank=True)
    synthesis_data = JSONField(default=dict)  # Full synthesis output
    member_count = IntegerField(default=0)
    profile_ids_analyzed = JSONField(default=list)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**Service:** `intelligence/services/l2_synthesis_service.py` — `collect_l1_data()`, `build_synthesis_prompt()`, `run_synthesis()`
**Prompt:** `prompts/synthesis/l2_team_synthesis.md`
**API:** `POST /o/<slug>/il/api/t/<team_slug>/synthesis/` (trigger), `GET` (latest), `GET /o/<slug>/il/api/synthesis/<id>/` (poll)
**Page:** `/o/<slug>/il/t/<team_slug>/synthesis/`
**SQS Task:** `run_l2_synthesis` on `system_queue`

---

## 4. Core Files Reference

### Views & Templates

| File | Purpose |
|------|---------|
| `intelligence/views.py` | Main views (dashboard, employee detail, invite, interview) |
| `intelligence/api_views.py` | REST API endpoints |
| `intelligence/urls.py` | URL routing |
| `intelligence/templates/intelligence/dashboard.html` | Company dashboard |
| `intelligence/templates/intelligence/employee_detail.html` | Employee detail page |
| `intelligence/templates/intelligence/interview.html` | Interview chat interface |
| `intelligence/templates/intelligence/automation_opportunities.html` | Automation dashboard |

### Services

| File | Purpose |
|------|---------|
| `intelligence/services/interview_service.py` | Interview session management |
| `intelligence/services/hook_dispatcher.py` | Post-interview hook execution |
| `intelligence/services/synthetic_employee_service.py` | Synthetic employee profile generation |
| `intelligence/services/synthetic_interview_service.py` | AI-to-AI interview execution |
| `intelligence/services/opportunity_discussion_service.py` | Opportunity chat refinement |

### Models & Migrations

| File | Purpose |
|------|---------|
| `intelligence/models.py` | All data models |
| `intelligence/constants.py` | Synthetic employee archetypes |
| `intelligence/admin.py` | Django admin configuration |

### WebSocket

| File | Purpose |
|------|---------|
| `intelligence/consumers.py` | WebSocket consumers for real-time updates |

---

## 5. Interview System

### Interview Types

| Type | Purpose | Duration |
|------|---------|----------|
| **Mapping** | Broad discovery of role, responsibilities, tools | 15-30 min |
| **Deep Dive** | Detailed exploration of specific process | 20-45 min |

### Interview Flow

```
1. Employee clicks "Start Interview" (or picks from queue)
2. InterviewSession created (status='active')
3. AI sends greeting (based on interview type + any continuation context)
4. Employee and AI exchange messages (stored as InterviewMessage)
5. AI decides when complete OR employee ends session
6. Session marked 'completed' → Hooks triggered
```

### Continuation Interviews

If a mapping interview didn't cover everything, `future_interviews` hook recommends continuation:
- `is_continuation=True` on queue item
- `continuation_context` injected into greeting: "Last time we covered X. Let's continue with Y."

---

## 6. Post-Interview Hooks

When an interview ends, hooks run via SQS `system_queue`.

### Analyzers (Produce Data)

| Hook | Purpose | Output |
|------|---------|--------|
| `summary` | Brief 2-3 paragraph summary | `{summary, key_points}` |
| `session_report` | Coverage tracking | `{areas_covered, areas_not_covered}` |
| `future_interviews` | Recommend next interviews | `{recommended_next, continuation_context}` |
| `tool_extraction` | Systems/tools mentioned | `{tools: [...]}` |
| `people_mapping` | People/roles mentioned | `{people: [...]}` |
| `metrics` | Extract KPIs/metrics | `{metrics: [...]}` |
| `process_document` | Detailed process docs (deep dive only) | `{document: ...}` |

### Actions (Do Things)

| Hook | Depends On | Purpose |
|------|------------|---------|
| `queue_next_interviews` | `future_interviews` | Creates InterviewQueueItem records |
| `update_automation_opportunities` | `tool_extraction` | Updates EmployeeAutomationAnalysis |

### Hook Execution Flow

```
Interview Ends
      │
      ▼
HookDispatcher.dispatch_all(session)
      │
      ├── Create InterviewHookResult for each enabled hook
      ├── Queue hooks with no dependencies immediately
      └── Queue hooks with dependencies as 'waiting'
      │
      ▼
SQS Worker picks up hook task
      │
      ▼
HookDispatcher.run_hook(session_id, hook_id)
      │
      ├── Load prompt from file
      ├── Build context (transcript, employee info, previous results)
      ├── Call LLM
      ├── Parse response → save to InterviewHookResult
      └── Trigger dependent hooks if this one completed
```

### Prompt Files Location

```
prompts/
├── mapping_interview_prompt.md
├── deep_dive_interview_prompt.md
└── post-interview/
    ├── analyzers/
    │   ├── summary.md
    │   ├── session_report.md
    │   ├── future_interviews.md
    │   ├── tool_extraction.md
    │   ├── people_mapping.md
    │   └── metrics.md
    └── actions/
        ├── queue_next_interviews.md
        └── update_automation_opportunities.md
```

---

## 7. Automation Opportunities

### Concept

After each interview, ALL transcripts for that employee are analyzed to identify automation opportunities. This is cumulative - each interview refines the analysis.

### Analysis Flow

```
Interview Completes
      │
      ▼
tool_extraction hook runs first
      │
      ▼
update_automation_opportunities hook runs (depends on tool_extraction)
      │
      ├── Load ALL interview transcripts
      ├── Load ALL tool_extraction results
      ├── Load previous EmployeeAutomationAnalysis
      ├── Load available BigBongo integrations (ServiceDefinition)
      │
      ▼
LLM analyzes and returns:
      ├── opportunities[] - new or updated
      ├── conflicts[] - contradictory info across interviews
      └── analysis_notes
      │
      ▼
Save/Update AutomationOpportunity records
```

### Opportunity Scores

| Score | Values | Purpose |
|-------|--------|---------|
| **Time Per Run** | 1min, 5min, 15min, 30min, 1hr, 2hr, 4hr, 8hr | How long one manual execution takes |
| **Time Saved** | <1h, 1-2h, 2-4h, 4-8h, 8+h per week | Weekly value if automated |
| **Complexity** | Easy, Medium, Hard | Effort to build |
| **Frequency** | Daily, Weekly, Monthly, Occasional | How often task occurs |
| **Confidence** | High, Medium, Low | How certain is this suggestion |
| **Priority** | High, Medium, Low | Combined ranking |

### ROI Calculation

If employee has `annual_salary` set:
- `hourly_rate = annual_salary / 2000` (50 weeks × 40 hours)
- `annual_savings = hours_saved_per_week × 50 × hourly_rate`

---

## 8. Synthetic Employees

### Purpose

AI-generated employee personas for testing, demos, and training. Full interview chains run automatically (AI interviewer + AI interviewee).

### Archetypes (10 Predefined)

| # | Job Title | Description |
|---|-----------|-------------|
| 1 | Freelance Tech Recruiter | Solo recruiter with candidate tracking |
| 2 | Operations Manager | Ops lead with spreadsheets, reports |
| 3 | Marketing Coordinator | Social media, email campaigns |
| 4 | Customer Support Lead | Tickets, escalations, knowledge base |
| 5 | Finance Analyst | Monthly reporting, data consolidation |
| 6 | HR Generalist | Onboarding, benefits, compliance |
| 7 | Sales Development Rep | Lead qualification, CRM, outreach |
| 8 | Project Coordinator | Task tracking, status updates |
| 9 | E-commerce Store Owner | Orders, inventory, customer inquiries |
| 10 | Executive Assistant | Calendar, travel, expense reports |

### Resistance Level (1-10)

Controls how cooperative the synthetic persona is:
- **1-2**: Fully cooperative, shares everything
- **3-4**: Open, answers thoroughly
- **5-6**: Neutral, some hesitation
- **7-8**: Guarded, minimal responses
- **9-10**: Protective, deflects questions

### Synthetic Interview Flow

```
User clicks "Generate Interviews" on synthetic employee
      │
      ▼
Queue initial mapping interview
      │
      ▼
SyntheticInterviewService.run_interview_chain()
      │
      ├── Start mapping interview
      ├── Turn-by-turn: Interviewer AI ←→ Persona AI
      ├── Interview ends (max 100 questions)
      ├── Hooks run → may queue deep dives
      ├── Pick next from queue
      └── Continue until queue empty
```

---

## 9. Invitation System

### Unified Invitation Model

Located in `accounts/models.py`:

```python
class Invitation(models.Model):
    TYPE_CHOICES = [
        ('org_admin', 'Organization Admin'),
        ('company_admin', 'Intelligence Company Admin'),
        ('employee', 'Employee'),
    ]

    email = models.EmailField()
    name = models.CharField()
    invitation_type = models.CharField(choices=TYPE_CHOICES)
    status = models.CharField(choices=['pending', 'accepted', 'expired', 'cancelled'])
    token = models.CharField(unique=True)  # Magic link token
    expires_at = models.DateTimeField()

    organization = models.ForeignKey(Organization, null=True)  # For org_admin
    company = models.ForeignKey(Company, null=True)  # For company_admin/employee
    metadata = models.JSONField()  # job_title for employees, etc.
```

### Invitation Flow

```
1. Admin invites employee via form
2. Invitation created with unique token
3. Email sent with magic link: /accounts/invite/{token}/
4. Employee clicks link → sets password
5. User created, Employee linked, logged in
```

---

## 10. WebSocket Real-Time Updates

### Connection

```
ws://{host}/ws/intelligence/company/{company_id}/
```

### Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `get_synthetic_status` | Client → Server | Request current synthetic interview status |
| `synthetic_status` | Server → Client | Full status update for all synthetic employees |
| `synthetic_interview_update` | Server → Client | Interview started/completed/progress |

### Dashboard WebSocket Integration

The dashboard (`dashboard.html`) connects via WebSocket to get real-time updates on synthetic interview generation status.

---

## 11. API Endpoints

### Company & Employees

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/intelligence/companies/` | GET | List user's companies |
| `/api/intelligence/companies/{id}/` | GET | Company detail |
| `/api/intelligence/companies/{id}/employees/` | GET | List employees |
| `/api/intelligence/employees/{id}/` | GET | Employee detail |

### Units (Teams)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/intelligence/companies/{id}/units/` | GET, POST | List/create units |
| `/api/intelligence/units/{id}/` | PATCH, DELETE | Update/delete unit |

### Interviews

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/intelligence/sessions/{id}/` | GET | Session detail |
| `/api/intelligence/sessions/{id}/messages/` | GET, POST | List/send messages |
| `/api/intelligence/sessions/{id}/end/` | POST | End session |

### Automation Opportunities

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/intelligence/employees/{id}/automation/` | GET | Employee automation dashboard |
| `/api/intelligence/opportunities/{id}/` | GET, PATCH | Opportunity detail/update |
| `/api/intelligence/employees/{id}/automation/reanalyze/` | POST | Trigger re-analysis |

---

## 12. URL Routes

### Main Intelligence URLs (`/intelligence/...`)

| URL | View | Purpose |
|-----|------|---------|
| `/intelligence/company/{id}/dashboard/` | `dashboard` | Company dashboard |
| `/intelligence/company/{id}/employees/` | `employee_list` | Employee list |
| `/intelligence/company/{id}/employees/{eid}/` | `employee_detail` | Employee detail |
| `/intelligence/company/{id}/invite/` | `invite_employee` | Invite employee form |
| `/intelligence/company/{id}/units/` | `manage_units` | Manage org units |
| `/intelligence/interview/` | `interview_landing` | Employee's interview landing |
| `/intelligence/interview/{sid}/` | `interview_session` | Active interview |
| `/intelligence/company/{id}/employees/{eid}/automation/` | `automation_opportunities` | Automation dashboard |

### Synthetic Employee URLs

| URL | View | Purpose |
|-----|------|---------|
| `/intelligence/company/{id}/synthetic/create/` | `create_synthetic_employee` | Create synthetic |
| `/intelligence/company/{id}/synthetic/{eid}/edit/` | `edit_synthetic_employee` | Edit synthetic |
| `/intelligence/company/{id}/synthetic/{eid}/generate/` | `generate_synthetic_interviews` | Start interview chain |
| `/intelligence/company/{id}/synthetic/{eid}/stop/` | `stop_synthetic_interviews` | Stop interview chain |
| `/intelligence/company/{id}/synthetic/{eid}/delete/` | `delete_synthetic_employee` | Delete synthetic |

---

## 13. Prompts

### Interview Prompts

| File | Purpose |
|------|---------|
| `prompts/mapping_interview_prompt.md` | System prompt for mapping interviews |
| `prompts/deep_dive_interview_prompt.md` | System prompt for deep dive interviews |
| `prompts/mapping_interview_summary_prompt.md` | Legacy summary generation |
| `prompts/deep_dive_interview_summary_prompt.md` | Legacy summary generation |

### Hook Prompts

Located in `prompts/post-interview/`:

**Analyzers:**
- `analyzers/summary.md`
- `analyzers/session_report.md`
- `analyzers/future_interviews.md`
- `analyzers/tool_extraction.md`
- `analyzers/people_mapping.md`
- `analyzers/metrics.md`
- `analyzers/process_document.md`

**Actions:**
- `actions/queue_next_interviews.md`
- `actions/update_automation_opportunities.md`

---

## 14. Related Specifications

| Spec | Description |
|------|-------------|
| `specs/56-intelligence-layer/` | Current planning & tasks |
| `specs/58-interview-orchestrator/` | Post-interview hooks system |
| `specs/59-setup-assistant-active-guidance/` | Setup assistant |
| `specs/59-unified-invitation-system/` | Invitation system |
| `specs/60-employee-automation-opportunities/` | Automation dashboard |
| `specs/61-automation-notifications/` | Notification system |
| `specs/62-automation-opportunity-definition/` | Opportunity data model |
| `specs/63-synthetic-interviews/` | Synthetic employee system |

---

## Quick Reference

### Common Queries

```python
# Get company's members with session counts
members = company.memberships.annotate(
    session_count=Count('interview_sessions')
)

# Get member's pending interviews
pending = InterviewQueueItem.objects.filter(
    membership=membership, status='pending'
).order_by('priority', 'created_at')

# Get automation opportunities for member
opportunities = AutomationOpportunity.objects.filter(
    analysis__membership=membership
).exclude(status='deprecated')

# Get completed hook results for a session
results = InterviewHookResult.objects.filter(
    session=session, status='completed'
)

# Get synthetic persona for a membership
persona = getattr(membership, 'synthetic_persona', None)
```

### Key Checks

```python
# Is member synthetic?
if membership.is_synthetic:
    persona = membership.synthetic_persona
    # Access persona fields: persona.resistance_level, persona.background, etc.

# Is interview in progress?
if session.status == 'active':
    # Handle active session

# Does member have pending interviews?
if membership.interview_queue.filter(status='pending').exists():
    # Show queue to member
```

---

## Environment Notes

- WebSocket requires Redis for Django Channels
- Synthetic interviews use Opus model for both roles
- Hooks run via SQS `system_queue` (not separate queue)
- Prompts are file-based (not in database)
