# Suna Ultra - Self-Hosting Guide

Complete guide for self-hosting Suna Ultra on your own server, including home servers.

## 🏠 Why Self-Host?

### Benefits

- **🔒 Privacy**: Keep your data on your infrastructure
- **💰 Cost Control**: No subscription fees, use free local LLMs
- **🎛️ Customization**: Full control over configuration and features
- **🚀 Performance**: Optimize for your specific workload
- **📊 Data Ownership**: Complete control over your data

### Use Cases

- Personal AI assistant running 24/7
- Team collaboration with private deployment
- Development and testing environment
- Learning platform for AI/ML
- Small business automation

## 📋 Requirements

### Hardware

#### Minimum Configuration

- **CPU**: 2 cores (x86_64)
- **RAM**: 8GB
- **Storage**: 20GB SSD
- **Network**: Stable internet connection

#### Recommended Configuration

- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD
- **Network**: Gigabit ethernet or fast WiFi

#### Ideal Configuration

- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 100GB+ NVMe SSD
- **Network**: Wired gigabit ethernet
- **GPU**: Optional, for local LLM acceleration

### Software

- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Raspberry Pi OS
- **Docker**: 20.10+
- **Docker Compose**: v2.0+
- **Git**: 2.x

### Network

- **Ports**: 80, 443 (or custom)
- **Domain**: Optional, but recommended for SSL
- **Dynamic DNS**: If using home internet

## 🚀 Installation

### Method 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/Danthemainman1/suna-enhanced.git
cd suna-enhanced

# Run setup
cd deploy/scripts
./setup.sh
```

The script will:
1. Check dependencies (Docker, Docker Compose)
2. Create `.env` file with secure secrets
3. Prompt for API keys
4. Pull and build Docker images
5. Start all services
6. Verify health

### Method 2: Manual Setup

#### 1. Clone Repository

```bash
git clone https://github.com/Danthemainman1/suna-enhanced.git
cd suna-enhanced
```

#### 2. Configure Environment

```bash
cd deploy/docker
cp .env.example .env
```

Edit `.env`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)

# Supabase (Required)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=xxx

# Optional
OPENAI_API_KEY=
DOMAIN=localhost
```

#### 3. Start Services

```bash
docker compose -f docker-compose.prod.yml up -d
```

#### 4. Verify

```bash
curl http://localhost/health
```

## 🔧 Configuration

### Environment Variables

#### Required Variables

```bash
# LLM Provider (at least one)
ANTHROPIC_API_KEY=sk-ant-xxx

# Database (Supabase)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=xxx

# Security
SECRET_KEY=<64-character-hex>
DB_PASSWORD=<32-character-random>
```

#### Optional Variables

```bash
# Additional LLM Providers
OPENAI_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=

# Server
DOMAIN=yourdomain.com

# Integrations
RAPID_API_KEY=
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
```

### Supabase Setup

Suna Ultra uses Supabase for authentication and data storage.

#### Option 1: Cloud Supabase (Recommended)

1. **Sign up**: https://supabase.com
2. **Create project**: New project → Choose region
3. **Get credentials**: Settings → API
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_ANON_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`
   - JWT Secret → `SUPABASE_JWT_SECRET`

#### Option 2: Self-Hosted Supabase

See [Supabase Self-Hosting Guide](https://supabase.com/docs/guides/self-hosting)

### Resource Allocation

Edit `docker-compose.prod.yml` to adjust resources:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M  # Adjust based on RAM
          cpus: '0.5'   # Adjust based on CPU cores
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Worker Scaling

Adjust worker count based on workload:

```yaml
worker:
  deploy:
    replicas: 2  # Increase for more concurrent tasks
```

Or scale dynamically:

```bash
docker compose up -d --scale worker=4
```

## 🌐 Remote Access

### Port Forwarding

Configure your router to forward ports to your server:

1. **Login to router**: Usually http://192.168.1.1
2. **Port Forwarding section**: Often under Advanced/NAT
3. **Add rules**:
   - External Port 80 → Internal IP:80
   - External Port 443 → Internal IP:443

### Dynamic DNS

If you have a dynamic IP:

#### No-IP (Free)

```bash
# Sign up at https://www.noip.com
# Create hostname (e.g., mysuna.ddns.net)

# Install DUC
wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz
tar xzf noip-duc-linux.tar.gz
cd noip-2.1.9
make
sudo make install

# Configure
sudo /usr/local/bin/noip2 -C

# Start
sudo /usr/local/bin/noip2
```

#### DuckDNS (Free)

```bash
# Sign up at https://www.duckdns.org
# Create subdomain (e.g., mysuna.duckdns.org)

# Get token from dashboard
TOKEN=your-token-here
SUBDOMAIN=mysuna

# Install updater
mkdir -p ~/duckdns
cd ~/duckdns
echo "echo url=\"https://www.duckdns.org/update?domains=$SUBDOMAIN&token=$TOKEN&ip=\" | curl -k -o ~/duckdns/duck.log -K -" > duck.sh
chmod 700 duck.sh

# Add to crontab
crontab -e
# Add: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

### Cloudflare Tunnel (Recommended)

No port forwarding needed!

```bash
# Install cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create suna-ultra

# Configure tunnel
cat > ~/.cloudflared/config.yml <<EOF
url: http://localhost:80
tunnel: suna-ultra
credentials-file: /root/.cloudflared/<tunnel-id>.json
EOF

# Route DNS
cloudflared tunnel route dns suna-ultra yourdomain.com

# Start tunnel
cloudflared tunnel run suna-ultra
```

Make it a service:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## 🔒 SSL/TLS Setup

### Let's Encrypt (Free, Recommended)

#### Prerequisites

- Domain name pointing to your server
- Ports 80 and 443 open

#### Installation

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Stop nginx temporarily
docker compose -f deploy/docker/docker-compose.prod.yml stop nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Certificate location:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### Configure nginx

```bash
# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
  deploy/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem \
  deploy/docker/nginx/ssl/key.pem

# Make readable by nginx
sudo chmod 644 deploy/docker/nginx/ssl/cert.pem
sudo chmod 600 deploy/docker/nginx/ssl/key.pem
```

Edit `deploy/docker/nginx/nginx.conf`:
- Uncomment HTTPS server block
- Update `server_name` to your domain

```bash
# Restart nginx
docker compose -f deploy/docker/docker-compose.prod.yml start nginx
```

#### Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "cd /path/to/deploy/docker && docker compose restart nginx"
```

### Self-Signed Certificate (Testing Only)

```bash
cd deploy/docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/CN=localhost"
```

## 💾 Backup & Disaster Recovery

### Automated Backups

```bash
# Test backup
cd deploy/scripts
./backup.sh ./backups

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/deploy/scripts/backup.sh /backups/suna-ultra
```

### Backup Storage

#### Local Backup

```bash
# Keep 7 days of backups
find /backups/suna-ultra -name "db_*.sql" -mtime +7 -delete
find /backups/suna-ultra -name "redis_*.rdb" -mtime +7 -delete
```

#### Remote Backup

```bash
# rsync to remote server
rsync -avz /backups/suna-ultra/ user@backup-server:/backups/

# Or use rclone for cloud storage
rclone sync /backups/suna-ultra remote:suna-backups
```

### Disaster Recovery

```bash
# Restore from backup
cd deploy/scripts
./restore.sh /backups/suna-ultra/db_20240101_120000.sql

# Restart services
docker compose -f deploy/docker/docker-compose.prod.yml restart
```

## 📊 Monitoring

### Health Checks

```bash
# Manual check
cd deploy/scripts
./health-check.sh

# Automated monitoring (add to crontab)
*/5 * * * * /path/to/deploy/scripts/health-check.sh || echo "Suna Ultra is down!" | mail -s "Alert" admin@example.com
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Disk usage
docker system df
df -h

# Memory usage
free -h
```

### Log Management

```bash
# View logs
docker compose -f deploy/docker/docker-compose.prod.yml logs -f

# Log rotation
# Add to /etc/docker/daemon.json:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Restart Docker
sudo systemctl restart docker
```

## 🔧 Maintenance

### Updates

```bash
# Pull latest code
cd /path/to/suna-enhanced
git pull origin main

# Update with zero downtime
cd deploy/scripts
./deploy.sh
```

### Database Maintenance

```bash
# Vacuum PostgreSQL
docker compose exec postgres vacuumdb -U suna -d suna_ultra -z -v

# Optimize Redis
docker compose exec redis redis-cli BGREWRITEAOF
```

### Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## 🏠 Home Server Setup

### Raspberry Pi

Suna Ultra can run on Raspberry Pi 4 (8GB):

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Increase swap (recommended)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Clone and setup
git clone https://github.com/Danthemainman1/suna-enhanced.git
cd suna-enhanced/deploy/scripts
./setup.sh
```

### NAS/Home Server

#### Synology

1. Install Docker package from Package Center
2. Enable SSH: Control Panel → Terminal & SNMP
3. SSH into NAS and follow standard installation

#### Unraid

1. Install Docker via Apps
2. Create custom container or use docker compose
3. Map volumes to array

### Power Management

```bash
# Auto-start on boot
sudo systemctl enable docker

# Auto-restart containers
# Already configured in docker-compose.prod.yml:
restart: always
```

## 🔐 Security

### Firewall

```bash
# UFW (Ubuntu/Debian)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Fail2ban (optional)
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

### SSH Security

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd

# Use key-based authentication only
ssh-keygen -t ed25519
ssh-copy-id user@server
```

### Docker Security

```bash
# Run as non-root user
sudo usermod -aG docker $USER

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scan suna-ultra/backend:latest
```

### API Security

1. **Change default secrets** in `.env`
2. **Use HTTPS** in production
3. **Implement rate limiting** (configured in nginx)
4. **Regular updates** for security patches

## ❓ Troubleshooting

### Services Won't Start

```bash
# Check Docker
sudo systemctl status docker

# Check logs
docker compose -f deploy/docker/docker-compose.prod.yml logs

# Reset everything (⚠️ data loss)
docker compose -f deploy/docker/docker-compose.prod.yml down -v
cd deploy/scripts && ./setup.sh
```

### Out of Memory

```bash
# Check memory
free -h

# Reduce workers
docker compose up -d --scale worker=1

# Adjust limits in docker-compose.prod.yml
```

### Slow Performance

```bash
# Check resources
docker stats

# Increase resources
# Edit docker-compose.prod.yml

# Use SSD storage
# Move Docker data to SSD
```

### Can't Access Remotely

```bash
# Check firewall
sudo ufw status

# Check port forwarding
curl http://your-public-ip

# Check logs
docker compose logs nginx
```

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [Docker Deployment Guide](../deploy/docker/README.md)
- [Kubernetes Guide](../deploy/kubernetes/README.md)
- [API Documentation](http://localhost/docs)

## 🆘 Support

- **GitHub Issues**: [Report bugs](https://github.com/Danthemainman1/suna-enhanced/issues)
- **Discord**: [Join community](https://discord.gg/RvFhXUdZ9H)
- **Twitter**: [@kortix](https://x.com/kortix)

## 📄 License

Apache License 2.0 - See [LICENSE](../LICENSE)

---

**Happy self-hosting! 🏠🚀**

Questions? Join our [Discord community](https://discord.gg/RvFhXUdZ9H)
