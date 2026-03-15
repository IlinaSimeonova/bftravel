# Project Notes

## Server Access

- SSH access to the server is available
- Connection: `ssh server` (uses alias from ~/.ssh/config)
- Host: 157.173.109.52
- User: root
- Key: ~/.ssh/id_ed25519_server

## Domain

- Domain: bauernfeind.travel
- DNS: Cloudflare (user has account)


## Project Structure

```
/var/www/bauernfeind.travel/
├── app/                 # Django project (cloned from git)
├── venv/                # virtualenv with Python 3.12
├── static/              # Collected static files
├── media/               # User uploads
├── logs/                # Gunicorn logs
└── gunicorn.sock        # Unix socket for Gunicorn
```

## Services

### Gunicorn
- Service: `bftravel.service`
- Socket: `bftravel.socket`
- Start: `systemctl start bftravel`
- Status: `systemctl status bftravel`
- Logs: `/var/www/bauernfeind.travel/logs/`

### Nginx
- Config: `/etc/nginx/sites-available/bauernfeind.travel`
- Test: `nginx -t`
- Reload: `systemctl reload nginx`

## Deployment Commands

```bash
# Pull latest code
cd /var/www/bauernfeind.travel/app && git pull

# Install new dependencies
/var/www/bauernfeind.travel/venv/bin/pip install -r requirements.txt

# Run migrations
/var/www/bauernfeind.travel/venv/bin/python manage.py migrate

# Collect static files
/var/www/bauernfeind.travel/venv/bin/python manage.py collectstatic --noinput

# Restart Gunicorn
systemctl restart bftravel
```

## Cloudflare SSL

- DNS: A records pointing to 157.173.109.52 (proxied)
- SSL/TLS Mode: Full
- Cloudflare handles SSL certificates automatically

## Firewall (UFW)

- Status: Active
- Allowed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Django Admin

- URL: https://bauernfeind.travel/admin/
- Email: ilina96@gmail.com
- Password: admin123 (change this after first login)
