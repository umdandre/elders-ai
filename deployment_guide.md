# Elder Care AI MVP - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Elder Care AI MVP to production environments. The application consists of three main components: Flask backend API, React elder mobile app, and React caregiver dashboard.

## Prerequisites

### System Requirements
- **Server**: Ubuntu 20.04+ or similar Linux distribution
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 20GB available disk space
- **CPU**: 2 cores minimum (4 cores recommended)
- **Network**: Public IP address with ports 80/443 available

### Software Dependencies
- **Python**: 3.11+
- **Node.js**: 20.18.0+
- **PostgreSQL**: 14+ (for production database)
- **Nginx**: Latest stable version
- **SSL Certificate**: Let's Encrypt or commercial certificate

## Backend Deployment

### 1. Server Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash eldercare
sudo usermod -aG sudo eldercare
```

### 2. Database Configuration
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE eldercare_db;
CREATE USER eldercare_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE eldercare_db TO eldercare_user;
\q
```

### 3. Application Deployment
```bash
# Switch to application user
sudo su - eldercare

# Clone or upload application code
git clone <repository_url> /home/eldercare/elder-care-app
cd /home/eldercare/elder-care-app/backend/elder-care-api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configure environment variables
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your_super_secure_secret_key_here
DATABASE_URL=postgresql://eldercare_user:secure_password_here@localhost/eldercare_db
UBER_API_KEY=your_uber_api_key
GOOGLE_CALENDAR_API_KEY=your_google_api_key
FITBIT_CLIENT_ID=your_fitbit_client_id
EOF

# Initialize database
python src/main.py db init
python src/main.py db migrate
python src/main.py db upgrade
```

### 4. Gunicorn Configuration
```bash
# Create Gunicorn configuration
cat > /home/eldercare/elder-care-app/backend/elder-care-api/gunicorn.conf.py << EOF
bind = "127.0.0.1:5001"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# Create systemd service
sudo cat > /etc/systemd/system/eldercare-api.service << EOF
[Unit]
Description=Elder Care API
After=network.target

[Service]
User=eldercare
Group=eldercare
WorkingDirectory=/home/eldercare/elder-care-app/backend/elder-care-api
Environment=PATH=/home/eldercare/elder-care-app/backend/elder-care-api/venv/bin
ExecStart=/home/eldercare/elder-care-app/backend/elder-care-api/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable eldercare-api
sudo systemctl start eldercare-api
```

## Frontend Deployment

### 1. Elder Mobile App
```bash
# Navigate to elder app directory
cd /home/eldercare/elder-care-app/frontend/elder-care-mobile

# Install dependencies
npm install

# Configure production API URL
cat > .env.production << EOF
VITE_API_BASE_URL=https://api.eldercare.yourdomain.com
EOF

# Build for production
npm run build

# Copy build files to web directory
sudo mkdir -p /var/www/eldercare-mobile
sudo cp -r dist/* /var/www/eldercare-mobile/
sudo chown -R www-data:www-data /var/www/eldercare-mobile
```

### 2. Caregiver Dashboard
```bash
# Navigate to caregiver dashboard directory
cd /home/eldercare/elder-care-app/frontend/caregiver-dashboard

# Install dependencies
npm install

# Configure production API URL
cat > .env.production << EOF
VITE_API_BASE_URL=https://api.eldercare.yourdomain.com
EOF

# Build for production
npm run build

# Copy build files to web directory
sudo mkdir -p /var/www/eldercare-dashboard
sudo cp -r dist/* /var/www/eldercare-dashboard/
sudo chown -R www-data:www-data /var/www/eldercare-dashboard
```

## Nginx Configuration

### 1. API Server Configuration
```bash
sudo cat > /etc/nginx/sites-available/eldercare-api << EOF
server {
    listen 80;
    server_name api.eldercare.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
```

### 2. Mobile App Configuration
```bash
sudo cat > /etc/nginx/sites-available/eldercare-mobile << EOF
server {
    listen 80;
    server_name app.eldercare.yourdomain.com;
    root /var/www/eldercare-mobile;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

### 3. Dashboard Configuration
```bash
sudo cat > /etc/nginx/sites-available/eldercare-dashboard << EOF
server {
    listen 80;
    server_name dashboard.eldercare.yourdomain.com;
    root /var/www/eldercare-dashboard;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

### 4. Enable Sites
```bash
# Enable sites
sudo ln -s /etc/nginx/sites-available/eldercare-api /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/eldercare-mobile /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/eldercare-dashboard /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## SSL Certificate Setup

### 1. Install SSL Certificates
```bash
# Install certificates for all domains
sudo certbot --nginx -d api.eldercare.yourdomain.com
sudo certbot --nginx -d app.eldercare.yourdomain.com
sudo certbot --nginx -d dashboard.eldercare.yourdomain.com

# Set up automatic renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Application Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Set up log rotation
sudo cat > /etc/logrotate.d/eldercare << EOF
/home/eldercare/elder-care-app/backend/elder-care-api/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 eldercare eldercare
}
EOF
```

### 2. Health Check Script
```bash
cat > /home/eldercare/health_check.sh << EOF
#!/bin/bash
# Health check script for Elder Care AI

# Check API health
API_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" https://api.eldercare.yourdomain.com/api/health)
if [ \$API_STATUS -ne 200 ]; then
    echo "API health check failed: \$API_STATUS"
    # Send alert (email, Slack, etc.)
fi

# Check database connection
DB_STATUS=\$(sudo -u eldercare psql -d eldercare_db -c "SELECT 1;" 2>/dev/null | grep -c "1 row")
if [ \$DB_STATUS -ne 1 ]; then
    echo "Database health check failed"
    # Send alert
fi

# Check disk space
DISK_USAGE=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "Disk usage high: \$DISK_USAGE%"
    # Send alert
fi
EOF

chmod +x /home/eldercare/health_check.sh

# Add to crontab for regular checks
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/eldercare/health_check.sh") | crontab -
```

## Security Configuration

### 1. Firewall Setup
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Security Headers
```bash
# Add security headers to Nginx
sudo cat >> /etc/nginx/nginx.conf << EOF
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
EOF

sudo systemctl restart nginx
```

## Backup Strategy

### 1. Database Backup
```bash
cat > /home/eldercare/backup_db.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/eldercare/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# Create database backup
pg_dump -h localhost -U eldercare_user eldercare_db > \$BACKUP_DIR/eldercare_db_\$DATE.sql

# Compress backup
gzip \$BACKUP_DIR/eldercare_db_\$DATE.sql

# Remove backups older than 30 days
find \$BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /home/eldercare/backup_db.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/eldercare/backup_db.sh") | crontab -
```

### 2. Application Backup
```bash
cat > /home/eldercare/backup_app.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/eldercare/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Backup application files
tar -czf \$BACKUP_DIR/eldercare_app_\$DATE.tar.gz /home/eldercare/elder-care-app

# Remove old application backups
find \$BACKUP_DIR -name "eldercare_app_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/eldercare/backup_app.sh

# Schedule weekly backups
(crontab -l 2>/dev/null; echo "0 3 * * 0 /home/eldercare/backup_app.sh") | crontab -
```

## Post-Deployment Verification

### 1. Functionality Tests
```bash
# Test API endpoints
curl https://api.eldercare.yourdomain.com/api/health
curl https://api.eldercare.yourdomain.com/api/integrations/config

# Test web applications
curl -I https://app.eldercare.yourdomain.com
curl -I https://dashboard.eldercare.yourdomain.com
```

### 2. Performance Tests
```bash
# Install Apache Bench for load testing
sudo apt install apache2-utils

# Test API performance
ab -n 100 -c 10 https://api.eldercare.yourdomain.com/api/health

# Test web app loading
ab -n 50 -c 5 https://app.eldercare.yourdomain.com/
```

## Troubleshooting

### Common Issues

1. **API not responding**
   ```bash
   sudo systemctl status eldercare-api
   sudo journalctl -u eldercare-api -f
   ```

2. **Database connection issues**
   ```bash
   sudo -u postgres psql -c "\l"
   sudo systemctl status postgresql
   ```

3. **Nginx configuration errors**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew --dry-run
   ```

### Log Locations
- **API Logs**: `/home/eldercare/elder-care-app/backend/elder-care-api/logs/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `/var/log/syslog`
- **Application Service**: `sudo journalctl -u eldercare-api`

## Maintenance

### Regular Tasks
- **Weekly**: Review application logs for errors
- **Monthly**: Update system packages and dependencies
- **Quarterly**: Review and rotate API keys
- **Annually**: Renew SSL certificates (if not automated)

### Monitoring Checklist
- [ ] API response times < 500ms
- [ ] Database query performance
- [ ] Disk space usage < 80%
- [ ] Memory usage < 80%
- [ ] SSL certificate validity
- [ ] Backup completion status
- [ ] Security update availability

This deployment guide provides a production-ready setup for the Elder Care AI MVP with proper security, monitoring, and backup procedures.

