# CharacterForge AI - Complete Deployment Guide

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose Setup](#docker-compose-setup)
3. [AWS Deployment](#aws-deployment)
4. [Production Checklist](#production-checklist)
5. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (optional, uses SQLite by default)
- Redis 7+ (optional, uses in-memory cache by default)
- Groq API Key

### Step 1: Setup

```bash
# Clone repository
git clone https://github.com/tfregixx/CharacterForge-AI.git
cd CharacterForge-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API key
nano .env
```

### Step 2: Run Services

**Terminal 1 - Backend API:**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
source venv/bin/activate
streamlit run app.py
```

Access:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Compose Setup

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM recommended

### Step 1: Configuration

```bash
# Clone repository
git clone https://github.com/tfregixx/CharacterForge-AI.git
cd CharacterForge-AI

# Copy environment
cp .env.example .env

# Edit with your keys
nano .env
```

### Step 2: Start Services

```bash
# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

### Step 3: Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Streamlit | http://localhost:8501 | - |
| FastAPI Backend | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| PGAdmin | http://localhost:5050 | admin@characterforge.local / admin |
| PostgreSQL | localhost:5432 | characterforge / characterforge_dev |
| Redis | localhost:6379 | - |

### Step 4: Database Management

```bash
# Connect to database
docker-compose exec postgres psql -U characterforge -d characterforge

# Create tables manually (if needed)
docker-compose exec backend python -c "from database.db import Base; Base.metadata.create_all()"

# Run migrations
docker-compose exec backend alembic upgrade head

# View database stats
docker-compose exec postgres psql -U characterforge -d characterforge \
  -c "SELECT schemaname, COUNT(*) FROM pg_tables GROUP BY schemaname;"
```

---

## AWS Deployment

### Prerequisites

- AWS Account with billing enabled
- AWS CLI configured
- Groq API Key
- Domain name (optional but recommended)

### Architecture

```
CloudFront CDN
     ↓
  EC2 Instance (Application)
     ↓
  RDS PostgreSQL (Database)
  ElastiCache Redis (Cache)
  S3 (Assets)
```

### Step 1: Prepare AWS Resources

```bash
# Configure AWS
aws configure

# Create S3 bucket for CloudFormation templates
aws s3 mb s3://characterforge-cfn-templates-$(aws sts get-caller-identity --query Account --output text)

# Upload templates
aws s3 cp deployment/cloudformation/ s3://characterforge-cfn-templates-*/
```

### Step 2: Run Deployment Script

```bash
# Make script executable
chmod +x deployment/deploy.sh

# Deploy to us-east-1
./deployment/deploy.sh characterforge us-east-1

# Or deploy to different region
./deployment/deploy.sh characterforge eu-west-1
```

### Step 3: Configure Environment

```bash
# Get EC2 instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=characterforge" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Your application: http://$PUBLIC_IP:8501"
```

### Step 4: Store Secrets

```bash
# Store Groq API key in AWS Secrets Manager
aws secretsmanager create-secret \
  --name characterforge/groq-api-key \
  --secret-string "your-groq-api-key"

# Store database password
aws secretsmanager create-secret \
  --name characterforge/db-password \
  --secret-string "your-secure-password"

# Store JWT secret
aws secretsmanager create-secret \
  --name characterforge/secret-key \
  --secret-string "your-jwt-secret-key"
```

### Step 5: Update EC2 User Data

SSH into your EC2 instance and update environment variables:

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@$PUBLIC_IP

# Update .env
sudo nano /home/ec2-user/CharacterForge-AI/.env

# Restart services
sudo systemctl restart characterforge-api
sudo systemctl restart characterforge-app
```

### Step 6: Configure Domain (Optional)

```bash
# Get CloudFront domain
aws cloudformation describe-stacks \
  --stack-name characterforge-cloudfront \
  --query 'Stacks[0].Outputs[?OutputKey==`DistributionDomain`].OutputValue' \
  --output text

# Create Route 53 record pointing to CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch file://route53-change.json
```

---

## Production Checklist

### Security

- [ ] Change all default passwords
- [ ] Enable SSL/TLS certificates (use AWS Certificate Manager)
- [ ] Configure security groups to allow only necessary ports
- [ ] Enable database encryption at rest and in transit
- [ ] Use VPC endpoints for S3 access
- [ ] Enable CloudTrail for AWS API logging
- [ ] Set up WAF (Web Application Firewall) rules
- [ ] Enable MFA on AWS account
- [ ] Rotate API keys regularly

### Performance

- [ ] Enable CloudFront caching
- [ ] Configure ElastiCache eviction policies
- [ ] Set up RDS read replicas for high availability
- [ ] Use RDS Multi-AZ deployment
- [ ] Configure auto-scaling for EC2 (if expected high traffic)
- [ ] Enable connection pooling in FastAPI
- [ ] Monitor application performance with CloudWatch

### Monitoring

- [ ] Setup CloudWatch alarms for:
  - CPU usage
  - Memory usage
  - Database connections
  - Redis hit rate
  - HTTP errors
- [ ] Configure SNS notifications
- [ ] Enable enhanced monitoring for RDS
- [ ] Set up log retention policies

### Backup & Recovery

- [ ] Enable automated RDS backups
- [ ] Test backup restoration procedures
- [ ] Create AMI snapshots of EC2 instance
- [ ] Document disaster recovery procedures
- [ ] Set backup retention to 30 days

### Compliance

- [ ] Review data privacy policies
- [ ] Implement GDPR compliance (if serving EU users)
- [ ] Set up audit logging
- [ ] Document security procedures
- [ ] Create incident response plan

---

## Troubleshooting

### Docker Issues

**Container fails to start:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache
```

**Port already in use:**
```bash
# Find process using port
lsof -i :8501
lsof -i :8000

# Kill process
kill -9 PID

# Or change ports in docker-compose.yml
```

### Database Issues

**Connection refused:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
# Format: postgresql://user:password@host:5432/database

# Verify credentials
docker-compose exec postgres psql -U characterforge -c "\du"
```

**Out of disk space:**
```bash
# Check volume usage
docker volume ls
docker system df

# Clean up unused volumes
docker volume prune

# Or expand volume in AWS
```

### API Issues

**Auth token expired:**
```bash
# Login again to get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

**Rate limiting:**
```bash
# Check current limits
curl -i http://localhost:8000/api/characters

# Look for X-RateLimit headers

# Contact admin to increase limits if needed
```

### Performance Issues

**Slow responses:**
```bash
# Check backend logs for errors
docker-compose logs backend | grep ERROR

# Monitor resource usage
docker stats

# Check database query performance
docker-compose exec postgres psql -U characterforge -c "\timing"
```

**High memory usage:**
```bash
# Restart services
docker-compose restart

# Clear cache
redis-cli FLUSHALL

# Check for memory leaks in code
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend -f

# With timestamps
docker-compose logs --timestamps

# Last 100 lines
docker-compose logs --tail=100
```

### Performance Metrics

```bash
# CPU and memory
docker stats

# Network
docker container stats --no-stream

# Disk usage
docker system df
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec postgres psql -U characterforge

# Check active connections
SELECT * FROM pg_stat_activity;

# Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements;

# Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

---

## Useful Commands

```bash
# Scale services
docker-compose up -d --scale backend=3

# Execute command in container
docker-compose exec backend python -c "from database.db import *; Base.metadata.create_all()"

# Copy files from container
docker-compose cp backend:/app/exports ./local-exports

# Update dependencies
pip install -r requirements.txt --upgrade
docker-compose build --no-cache

# Clean everything
docker-compose down -v
docker system prune -a
```

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check GitHub Issues
4. Contact support team

---

**Last Updated**: 2026-06-06
