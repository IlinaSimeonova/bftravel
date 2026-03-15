---
name: stage-feature
description: Deploy current feature branch to staging via develop
---

Deploy current feature branch to staging with safe merge handling.

**Flow**: `feature-branch` → `develop` → `staging` → deploy to server

---

## Phase 1: Pre-Flight Checks (CRITICAL)

### 1.1 Check for Uncommitted Changes

```bash
git status --short
```

**If uncommitted changes exist**: STOP IMMEDIATELY. Ask user to commit or stash first. Do NOT proceed with uncommitted changes - they could be lost during branch switching.

### 1.2 Record Current Branch

```bash
git branch --show-current
```

Store this as `$FEATURE_BRANCH`.

**Validation**: If on `develop`, `staging`, or `main` → STOP. Tell user to switch to a feature branch first.

Confirm with user this is the branch they want to deploy.

### 1.3 Check for Duplicate Migrations (82+)

```bash
ls -la */migrations/00[8-9]*.py */migrations/0[1-9][0-9][0-9]*.py 2>/dev/null | awk -F'/' '{print $NF}' | cut -d'_' -f1 | sort | uniq -d
```

**If duplicates found**: STOP IMMEDIATELY and alert user. Do NOT proceed.

### 1.4 Read SSH Connection from .env

```bash
grep SSH_CONNECTION .env
```

Each developer adds their own SSH command to `.env` (with quotes):
```
SSH_CONNECTION="ssh -i your_key your_user@62.171.136.238"
```

Example:
```
SSH_CONNECTION="ssh -i bigbongo_key demetrios@62.171.136.238"
```

---

## Phase 2: Merge Feature → Develop

### 2.1 Fetch Latest from Remote

```bash
git fetch origin
```

### 2.2 Checkout and Update Develop

```bash
git checkout develop
git pull origin develop
```

### 2.3 Merge Feature Branch into Develop

```bash
git merge $FEATURE_BRANCH --no-edit
```

**⚠️ IF MERGE CONFLICT OCCURS**:
1. Run `git status` to show conflicting files
2. Run `git merge --abort` to safely abort
3. Return user to feature branch: `git checkout $FEATURE_BRANCH`
4. STOP and report:
   ```
   ❌ Merge conflict detected: feature → develop

   Conflicting files:
   - path/to/file1.py
   - path/to/file2.py

   To resolve manually:
   1. git checkout develop
   2. git merge $FEATURE_BRANCH
   3. Resolve conflicts in your editor
   4. git add . && git commit
   5. Re-run /stage-feature
   ```
5. Do NOT continue to next phases

**✅ IF MERGE SUCCEEDS**:
```bash
git push origin develop
```

---

## Phase 3: Merge Develop → Staging

### 3.1 Checkout and Update Staging

```bash
git checkout staging
git pull origin staging
```

### 3.2 Merge Develop into Staging

```bash
git merge develop --no-edit
```

**⚠️ IF MERGE CONFLICT OCCURS**:
1. Run `git status` to show conflicting files
2. Run `git merge --abort` to safely abort
3. Return user to feature branch: `git checkout $FEATURE_BRANCH`
4. STOP and report:
   ```
   ⚠️ Feature → Develop merge SUCCEEDED
   ❌ Develop → Staging merge FAILED (conflict)

   Conflicting files:
   - path/to/file1.py

   To resolve manually:
   1. git checkout staging
   2. git merge develop
   3. Resolve conflicts in your editor
   4. git add . && git commit
   5. Run /deploy-staging
   ```
5. Do NOT continue to next phases

**✅ IF MERGE SUCCEEDS**:
```bash
git push origin staging
```

---

## Phase 4: Deploy from Staging

### 4.1 Verify on Staging Branch

```bash
git branch --show-current
```

Must show `staging`. If not, something went wrong - STOP.

### 4.2 Run Deploy Script

```bash
./deploy_to_staging.sh
```

This script handles:
- Push to staging branch
- Create tag: `staging-YYYY-MM-DD-N`
- SSH to server and pull
- Install requirements
- Collect static files
- Run migrations
- Restart services (Gunicorn, Daphne, workers, Nginx)

---

## Phase 5: Post-Deploy Verification

### 5.1 Verify Staging is Responding

```bash
curl -s -o /dev/null -w "%{http_code}" https://staging.bigbongo.ai/
```

### 5.2 Quick Log Check

```bash
$SSH_CONNECTION "tail -20 /var/www/bigbongo-staging/_logs/debug.log"
```

Note: Uses `SSH_CONNECTION` from `.env` (see Phase 1.4)

### 5.3 Return to Feature Branch

```bash
git checkout $FEATURE_BRANCH
```

---

## Final Report

| Step | Status |
|------|--------|
| Uncommitted changes | ✅ Clean / ❌ Blocked |
| Feature branch | `$FEATURE_BRANCH` |
| Duplicate migrations | ✅ None / ❌ Blocked |
| Feature → Develop | ✅ Merged / ❌ Conflict |
| Develop → Staging | ✅ Merged / ❌ Conflict |
| Deploy script | ✅ / ❌ |
| Site responding | ✅ HTTP {code} / ❌ |
| Tag created | `staging-YYYY-MM-DD-N` |
| Returned to | `$FEATURE_BRANCH` |

**Staging URL**: https://staging.bigbongo.ai

---

## Important Rules

- **NEVER force merge** if there's a conflict - always abort and let user resolve
- **NEVER continue** to deploy phase if any merge failed
- **ALWAYS return** user to their original feature branch after any failure
- **ALWAYS push** after successful merges before moving to next phase
