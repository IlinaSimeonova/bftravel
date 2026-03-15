#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting bftravel deployment process...${NC}"

# Parse optional --ssh argument (default: server alias from ~/.ssh/config)
SSH_TARGET="server"
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
ssh $SSH_TARGET "bash -s" <<'EOF'
    set -e
    echo -e "\033[0;32mConnected to server\033[0m"

    # Project paths
    PROJECT_DIR="/var/www/bauernfeind.travel"
    APP_DIR="${PROJECT_DIR}/app"
    VENV_PYTHON="${PROJECT_DIR}/venv/bin/python"
    VENV_PIP="${PROJECT_DIR}/venv/bin/pip"

    # Navigate to app directory
    cd $APP_DIR
    echo -e "\033[0;32mChanged to app directory: $APP_DIR\033[0m"

    # Pull latest changes from main branch
    git checkout main
    git pull origin main
    echo -e "\033[0;32mPulled latest changes from main branch\033[0m"

    $VENV_PYTHON --version

    # Install/update requirements
    $VENV_PIP install -r requirements.txt
    echo -e "\033[0;32mInstalled/updated requirements\033[0m"

    # Collect static files
    $VENV_PYTHON manage.py collectstatic --noinput
    echo -e "\033[0;32mCollected static files\033[0m"

    # Run migrations
    $VENV_PYTHON manage.py migrate
    echo -e "\033[0;32mRan database migrations\033[0m"

    # Restart Gunicorn
    systemctl restart bftravel.service
    echo -e "\033[0;32mRestarted Gunicorn\033[0m"

    # Reload Nginx
    systemctl reload nginx.service
    echo -e "\033[0;32mReloaded Nginx\033[0m"

    # Check service status
    echo -e "\033[0;32mChecking service status:\033[0m"
    systemctl status bftravel.service --no-pager | grep Active || true
    systemctl status nginx.service --no-pager | grep Active || true
EOF

# 4. Deployment complete
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Tag: ${TAG_NAME}${NC}"
