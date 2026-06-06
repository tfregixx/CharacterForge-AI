#!/bin/bash

# CharacterForge AI - AWS Deployment Script
# This script deploys the application to AWS using CloudFormation, EC2, RDS, and S3

set -e

echo "🚀 CharacterForge AI - AWS Deployment"
echo "======================================"

# Configuration
STACK_NAME=${1:-"characterforge-stack"}
REGION=${2:-"us-east-1"}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "AWS Account: $AWS_ACCOUNT_ID"

# Step 1: Create S3 bucket for assets
echo "\n📦 Creating S3 bucket..."
S3_BUCKET="characterforge-${AWS_ACCOUNT_ID}-${REGION}"

aws s3api create-bucket \
    --bucket $S3_BUCKET \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION 2>/dev/null || echo "Bucket already exists"

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket $S3_BUCKET \
    --versioning-configuration Status=Enabled

# Step 2: Create RDS PostgreSQL database
echo "\n🗄️  Creating RDS PostgreSQL instance..."

aws cloudformation create-stack \
    --stack-name $STACK_NAME-rds \
    --template-body file://deployment/cloudformation/rds.yaml \
    --parameters ParameterKey=DBName,ParameterValue=characterforge \
    --region $REGION \
    --on-failure DELETE 2>/dev/null || echo "RDS stack already exists"

# Wait for RDS to be ready
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME-rds \
    --region $REGION 2>/dev/null || echo "Continuing..."

# Get RDS endpoint
RDS_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME-rds \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' \
    --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"

# Step 3: Create EC2 security group
echo "\n🔒 Creating security group..."

SECURITY_GROUP=$(aws ec2 create-security-group \
    --group-name characterforge-sg \
    --description "CharacterForge AI security group" \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || aws ec2 describe-security-groups \
    --filters Name=group-name,Values=characterforge-sg \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

# Allow inbound traffic
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP \
    --protocol tcp --port 8501 --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "Already authorized"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "Already authorized"

# Step 4: Create EC2 instance
echo "\n💻 Creating EC2 instance..."

# Create user data script
cat > /tmp/user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git docker

systemctl start docker
systemctl enable docker

# Clone repository
cd /home/ec2-user
git clone https://github.com/tfregixx/CharacterForge-AI.git
cd CharacterForge-AI

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables (from AWS Secrets Manager in production)
export DATABASE_URL="postgresql://user:password@${RDS_ENDPOINT}:5432/characterforge"
export REDIS_URL="redis://localhost:6379/0"
export GROQ_API_KEY="${GROQ_API_KEY}"

# Run FastAPI backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Run Streamlit frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x /tmp/user-data.sh

AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
    --region $REGION \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.xlarge \
    --key-name characterforge \
    --security-group-ids $SECURITY_GROUP \
    --user-data file:///tmp/user-data.sh \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text 2>/dev/null || aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=characterforge" \
    --region $REGION \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

echo "EC2 Instance ID: $INSTANCE_ID"

# Step 5: Create CloudFront distribution
echo "\n🌐 Creating CloudFront distribution..."

aws cloudformation create-stack \
    --stack-name $STACK_NAME-cloudfront \
    --template-body file://deployment/cloudformation/cloudfront.yaml \
    --parameters ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET \
    --region $REGION 2>/dev/null || echo "CloudFront stack already exists"

# Step 6: Create ElastiCache Redis
echo "\n⚡ Creating ElastiCache Redis..."

aws cloudformation create-stack \
    --stack-name $STACK_NAME-redis \
    --template-body file://deployment/cloudformation/redis.yaml \
    --region $REGION 2>/dev/null || echo "Redis stack already exists"

echo "\n✅ Deployment Complete!"
echo "====================================="
echo "EC2 Instance: $INSTANCE_ID"
echo "RDS Database: $RDS_ENDPOINT"
echo "S3 Bucket: $S3_BUCKET"
echo "Security Group: $SECURITY_GROUP"
echo "\nNext steps:"
echo "1. Configure your environment variables in AWS Secrets Manager"
echo "2. Get the EC2 public IP and access the application"
echo "3. Configure DNS records to point to CloudFront distribution"
