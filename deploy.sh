#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting CRM deployment process...${NC}"

# Parse optional --ssh argument (default: same server as bigbongo)
SSH_TARGET="root@62.171.136.238"
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssh)
            SSH_TARGET="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            exit 1
            ;;
    esac
done
echo -e "${YELLOW}SSH target: ${SSH_TARGET}${NC}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes:${NC}"
    git status --short
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment canceled.${NC}"
        exit 1
    fi
fi

# 1. Push to main (production branch)
echo -e "${YELLOW}Pushing to main branch for production...${NC}"
git push origin main

# 2. Create deployment tag
TODAY=$(date +%Y-%m-%d)
LAST_TAG=$(git tag -l "production-${TODAY}-*" | sort -V | tail -1)
if [ -z "$LAST_TAG" ]; then
    DEPLOYMENT_NUM=1
else
    DEPLOYMENT_NUM=$(echo $LAST_TAG | sed -n "s/.*production-${TODAY}-\([0-9]*\)/\1/p")
    DEPLOYMENT_NUM=$((DEPLOYMENT_NUM + 1))
fi
TAG_NAME="production-${TODAY}-${DEPLOYMENT_NUM}"
echo -e "${YELLOW}Creating deployment tag: ${TAG_NAME}${NC}"
git tag $TAG_NAME main
git push origin $TAG_NAME

# 3. SSH to server and run deployment steps
echo -e "${YELLOW}Connecting to the server and deploying...${NC}"
ssh $SSH_TARGET "sudo bash -s" <<'EOF'
    set -e
    echo -e "\033[0;32mConnected to server\033[0m"

    # Navigate to project directory
    cd /var/www/crm
    echo -e "\033[0;32mChanged to project directory\033[0m"

    # Set the SSH key explicitly
    SSH_KEY_PATH=/root/.ssh/for-github-from-contabo

    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo -e "\033[1;31mERROR: SSH key not found: $SSH_KEY_PATH\033[0m"
        exit 1
    fi

    # Make sure GitHub's host key is in known_hosts
    if ! grep -q "github.com" ~/.ssh/known_hosts; then
        ssh-keyscan github.com >> ~/.ssh/known_hosts
    fi

    # Initialize pyenv and activate Python version
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv init --path)"
    export PYENV_VERSION="crm-3-12-0"
    echo -e "\033[0;32mActivated Python environment: $PYENV_VERSION\033[0m"

    # Pull latest changes from main branch
    GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git checkout main
    GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git pull origin main
    echo -e "\033[0;32mPulled latest changes from main branch\033[0m"

    python --version

    # Install/update requirements
    python -m pip install -r requirements.txt
    echo -e "\033[0;32mInstalled/updated requirements\033[0m"

    # Collect static files
    python manage.py collectstatic --noinput
    echo -e "\033[0;32mCollected static files\033[0m"

    # Run migrations
    python manage.py migrate
    echo -e "\033[0;32mRan database migrations\033[0m"

    # Restart Gunicorn
    systemctl restart crm.service
    echo -e "\033[0;32mRestarted Gunicorn\033[0m"

    # Reload Nginx
    systemctl reload nginx.service
    echo -e "\033[0;32mReloaded Nginx\033[0m"

    # Check service status
    echo -e "\033[0;32mChecking service status:\033[0m"
    systemctl status crm.service --no-pager | grep Active || true
    systemctl status nginx.service --no-pager | grep Active || true
EOF

# 4. Deployment complete
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Tag: ${TAG_NAME}${NC}"
