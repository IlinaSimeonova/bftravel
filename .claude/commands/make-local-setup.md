---
name: make-local-setup
description: Set up local development environment (ENVIRONMENT variable + SQS queues)
---

Run the local development setup script:

1. Ask the user for their email address
2. Run the setup command with that email:

```bash
PYENV_VERSION=bigbongo-3-12-0 python manage.py setup_local_dev --email <USER_EMAIL>
```

This will:
- Extract username from email (e.g., john.doe@company.com → john-doe)
- Update .env ENVIRONMENT to dev-{username}
- Create SQS queues in AWS with that environment prefix
- Configure Dead Letter Queue routing

After running, remind the user to restart their Django server for changes to take effect.
