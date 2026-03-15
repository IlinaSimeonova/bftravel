---
name: deploy-staging
description: Deploy to staging server
---

Deploy current branch to staging with pre-flight checks.

## Configuration

Read SSH connection from `.env` file:
```bash
grep SSH_CONNECTION .env
```

Use this value (SSH_CONNECTION) for all SSH commands below.

## Pre-Flight Checks (CRITICAL)

### 1. Sync with Develop (MANDATORY)

**Always merge latest develop before deploying to prevent migration conflicts:**

```bash
git fetch origin develop
git merge origin/develop --no-edit
```

If merge conflicts occur, STOP and resolve them before proceeding.

### 2. Check for Duplicate Migrations

Use `find` instead of glob patterns (works in both bash and zsh):

```bash
find . -path '*/migrations/0*.py' -name '00[8-9]*.py' -o -path '*/migrations/0*.py' -name '0[1-9][0-9][0-9]*.py' 2>/dev/null | xargs -I{} basename {} | cut -d'_' -f1 | sort | uniq -d
```

**If duplicates found: STOP IMMEDIATELY and alert user. Do NOT proceed.**

Example of what duplicates look like:
```
0096  <-- This means two migrations start with 0096
```

### 3. Compare Local Migrations with Server

Check if any local migration files would conflict with already-applied migrations on staging:

```bash
# Get list of applied migrations on server
$SSH_CONNECTION "cd /var/www/bigbongo-staging && source /root/.pyenv/versions/bigbongo-3-12-0/bin/activate && python manage.py showmigrations --list 2>/dev/null | grep '\[X\]' | awk '{print \$2}'" > /tmp/server_migrations.txt

# Compare with local migration files
for app in automation intelligence integrations recorder accounts; do
  if [ -d "$app/migrations" ]; then
    ls -1 $app/migrations/0*.py 2>/dev/null | xargs -I{} basename {} .py
  fi
done | sort > /tmp/local_migrations.txt

# Show migrations that exist locally but not on server (will be applied)
echo "Migrations to be applied:"
comm -23 /tmp/local_migrations.txt /tmp/server_migrations.txt
```

Review the list of migrations to be applied. If unexpected, investigate before proceeding.

### 4. Check Git Status

```bash
git status --short
```

Report any uncommitted changes. Ask user if they want to proceed anyway.

### 5. Verify Current Branch

```bash
git branch --show-current
```

Confirm this is the branch they want to deploy.

## Deployment Steps

### 6. Run Deploy Script

```bash
./deploy_to_staging.sh
```

This script handles:
- Push to staging branch
- Create tag: `staging-YYYY-MM-DD-N`
- SSH to server
- Pull changes
- Install requirements
- Collect static files
- Run migrations
- Restart services (Gunicorn, Daphne, workers, Nginx)

### 7. Verify Deployment

After script completes, check staging is responding:

```bash
curl -s -o /dev/null -w "%{http_code}" https://staging.bigbongo.ai/
```

### 8. Quick Log Check

```bash
$SSH_CONNECTION "tail -20 /var/www/bigbongo-staging/_logs/debug.log"
```

## Report Format

| Check | Status |
|-------|--------|
| Develop merged | ✅/❌ |
| Duplicate migrations | ✅ None / ❌ Found |
| Git status | Clean / X uncommitted |
| Branch | {branch_name} |
| Deploy script | ✅/❌ |
| Site responding | ✅/❌ (HTTP {code}) |
| Tag created | staging-YYYY-MM-DD-N |

**Site URL**: https://staging.bigbongo.ai
