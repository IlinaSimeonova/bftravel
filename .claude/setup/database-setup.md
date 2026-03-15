# Database Setup

## Initial Setup

After cloning the repository and setting up your environment:

```bash
# Set up local development (configures ENVIRONMENT and creates SQS queues)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_local_dev

# Run migrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py migrate

# Load subscription features (required)
PYENV_VERSION=bigbongo-3-12-0 python manage.py populate_subscription_features

# Load integration definitions (required for integrations to work)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_integrations

# Set up Google OAuth (optional, requires GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in .env)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_google_oauth
```

## Local Development Setup

The `setup_local_dev` command configures your local environment:

```bash
# Interactive mode (will prompt for email)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_local_dev

# With email argument
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_local_dev --email john.doe@company.com

# Preview changes without applying
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_local_dev --dry-run
```

**What it does:**
1. Asks for your email address
2. Extracts the username (part before @)
3. Updates `.env` ENVIRONMENT to `dev-{username}` (e.g., `dev-john-doe`)
4. Creates SQS queues in AWS with that environment prefix:
   - `bigbongo-dev-{username}-build-queue`
   - `bigbongo-dev-{username}-run-queue`
   - `bigbongo-dev-{username}-system-queue`
   - `bigbongo-dev-{username}-dead-letter`
5. Configures Dead Letter Queue routing for failed messages

## Integration Setup

### Setup Integrations Command

The `setup_integrations` management command loads integration definitions from `integrations/integrations.txt`.

**Options:**
- `--reset`: Clear all existing integrations before importing
- `--dry-run`: Show what would be imported without actually importing

**Examples:**
```bash
# Load integrations (first time or to update)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_integrations

# Reset and reload all integrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_integrations --reset

# Preview what would be imported (dry run)
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_integrations --dry-run
```

**What it does:**
- Parses `integrations/integrations.txt` (30MB HTML file from Zapier)
- Extracts ~8,500+ integration definitions
- Creates ServiceDefinition records with popularity rankings
- Filters out Zapier-internal services
- Uses `update_or_create` for idempotency (safe to run multiple times)

**Note:** The `integrations.txt` file is not tracked in git (it's in `.gitignore`). You need to obtain it from:
- Another developer
- Production backup
- Re-scrape from Zapier (if needed)

## Factory Reset

Reset all workflow/automation data while preserving users, organizations, and credentials:

```bash
# Dry run to see what would be deleted
PYENV_VERSION=bigbongo-3-12-0 python manage.py factory_reset --dry-run

# Perform reset (requires --confirm)
PYENV_VERSION=bigbongo-3-12-0 python manage.py factory_reset --confirm

# Reset and reload integrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py factory_reset --confirm --load-integrations
```

**What gets deleted:**
- All workflows, nodes, executions
- LLM interactions
- Test data
- Error logs
- Workflow versions

**What gets preserved:**
- User accounts and profiles
- Organizations
- Stored credentials (integration connections)
- Slack user connections
- Subscription tier definitions
- Integration definitions (unless you use --load-integrations to refresh)

## Database Recreation (Full Reset)

If you need to completely recreate the database:

```bash
# Drop and recreate database
dropdb bigbongo_dev
createdb bigbongo_dev

# Run migrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py migrate

# Load required data
PYENV_VERSION=bigbongo-3-12-0 python manage.py populate_subscription_features
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_integrations
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_google_oauth

# Create superuser (optional)
PYENV_VERSION=bigbongo-3-12-0 python manage.py createsuperuser
```

## Troubleshooting

### "Integration file not found" error

The `integrations.txt` file is not in the repository. Get it from:
1. Another developer on the team
2. Download from production/staging server
3. Re-scrape from Zapier (contact team lead for process)

Place it in: `integrations/integrations.txt`

### Integrations showing as "Not Ready"

Integrations imported by `setup_integrations` have `ai_extraction_status='pending'` and no authentication methods configured. They will show as "Not Ready" in the UI until:
1. AI analysis determines their authentication methods, OR
2. You manually configure authentication methods for specific integrations

### Import is slow

Importing 8,500+ integrations takes 30-60 seconds. This is normal. The command shows progress every 1,000 integrations.
