# CharacterForge AI 🎭

An enterprise-grade AI-powered character generation and interaction platform built with Streamlit, FastAPI, Groq, SQLite, and cloud infrastructure.

## 🌟 Features Overview

### Phases 1-10: Core Platform
- ✨ **AI Character Generation** - Groq-powered character creation
- 💾 **Character Persistence** - SQLite/PostgreSQL database
- 📚 **Character Gallery** - Browse and manage characters
- 💬 **Interactive Chat** - Real-time conversations with characters
- 🧠 **Character Memory** - SQLite-backed character memory system
- 🎨 **Image Generation** - AI-powered character portraits
- 📥 **Export System** - JSON, TXT, PDF export
- 🎨 **Professional UI** - Dark fantasy theme with Streamlit
- 🐳 **Docker Support** - Containerized deployment
- 🚀 **Cloud Ready** - Streamlit Community Cloud deployment

### Phases 11-23: Enterprise Features

#### **Phase 11: User Authentication** ✅
- User registration and login
- JWT-based token authentication
- Password hashing with bcrypt
- Email validation
- Session management

#### **Phase 12: Character Versions** ✅
- Track character evolution over time
- Version history and comparison
- Rollback to previous versions
- Change tracking

#### **Phase 13: Character Relationships** ✅
- Define relationships between characters
- Support for: Friends, Enemies, Family, Guilds, Kingdoms
- Relationship visualization
- Network analysis

#### **Phase 14: RAG Lore System** ✅
- Knowledge base for world-building
- Context-aware recall with SQLite-backed memory
- Lore types: World History, Cities, Kingdoms, Artifacts, Wars, Characters
- Context-aware character responses

#### **Phase 15: FastAPI Backend** ✅
- RESTful API architecture
- Async/await support
- OpenAPI documentation
- Modular route design

#### **Phase 16: PostgreSQL Migration** ✅
- Production-grade database
- Multi-user support
- Transaction support
- Connection pooling

#### **Phase 17: Redis Caching** ✅
- In-memory caching layer
- Character data caching
- Chat response caching
- Search result caching
- Configurable TTL

#### **Phase 18: Character Analytics** ✅
- Track usage metrics
- Character view counts
- Chat event logging
- User engagement analytics
- Dashboard ready

#### **Phase 19: Admin Dashboard** ✅
- User management
- Character moderation
- Usage analytics
- System monitoring
- Admin controls

#### **Phase 20: CI/CD** ✅
- GitHub Actions pipeline
- Automated testing
- Docker build and push
- Security scanning
- Automated deployment

#### **Phase 21: AWS Deployment** ✅
- CloudFormation infrastructure templates
- EC2 for application hosting
- RDS for PostgreSQL database
- S3 for asset storage
- CloudFront for CDN
- ElastiCache for Redis
- Automated deployment script

#### **Phase 22: LoRA Fine-Tuning** ✅
- Custom model training
- PEFT library integration
- Character-specific models
- SafeTensors format support

#### **Phase 23: SDXL + ControlNet Pipeline** ✅
- Advanced image generation
- SDXL Turbo model
- ControlNet for structure control
- Face restoration
- Image upscaling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         CloudFront CDN / Load Balancer              │
└────────────────┬────────────────────────────────────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
┌───▼──────────────┐    ┌──────▼──────────────┐
│  Streamlit App   │    │   FastAPI Backend   │
│   (Port 8501)    │    │    (Port 8000)      │
└───┬──────────────┘    └──────┬──────────────┘
    │                          │
    └────────────┬─────────────┘
                 │
    ┌────────────┼──────────────┐
    │            │              │
┌───▼────────┐  ┌┴─────────┐  ┌┴──────────┐
│PostgreSQL  │  │  Redis   │  │ SQLite    │
│  (RDS)     │  │  Cache   │  │ Local DB  │
└────────────┘  └──────────┘  └───────────┘
                 │
            ┌────▼─────┐
            │ S3/Assets │
            └───────────┘
```

## 📋 Project Structure

```
CharacterForge-AI/
├── app.py                              # Streamlit main application
├── backend/
│   ├── main.py                        # FastAPI application
│   ├── routes/
│   │   └── auth.py                   # Authentication routes
│   └── models/
│       └── schemas.py                # Pydantic schemas
│
├── services/
│   ├── character_generator.py        # Groq character generation
│   ├── chat_service.py               # Interactive chat
│   ├── memory_service.py             # SQLite-backed memory
│   ├── lore_service.py               # RAG/Lore system
│   ├── cache_service.py              # Redis caching
│   ├── auth_service.py               # Authentication utilities
│   ├── image_generator.py            # Basic image generation
│   ├── advanced_image_service.py     # SDXL + ControlNet
│   ├── export_service.py             # Multi-format export
│
├── database/
│   └── db.py                         # SQLAlchemy models and functions
│
├── deployment/
│   ├── deploy.sh                     # AWS deployment script
│   └── cloudformation/
│       ├── rds.yaml                  # PostgreSQL template
│       ├── redis.yaml                # Redis template
│       └── cloudfront.yaml           # CloudFront template
│
├── .github/
│   └── workflows/
│       └── deploy.yml                # CI/CD pipeline
│
├── docker-compose.yml                # Multi-container orchestration
├── Dockerfile                        # Application container
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
└── README.md                         # This file
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/tfregixx/CharacterForge-AI.git
cd CharacterForge-AI

# Copy environment template
cp .env.example .env

# Add your API key
# Edit .env and add: GROQ_API_KEY=your_key_here

# Start all services
docker-compose up

# Access applications
# Streamlit Frontend: http://localhost:8501
# FastAPI Backend: http://localhost:8000
# Backend Docs: http://localhost:8000/docs
# PGAdmin: http://localhost:5050
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env
# Edit .env with your keys

# Start backend (Terminal 1)
uvicorn backend.main:app --reload

# Start frontend (Terminal 2)
streamlit run app.py
```

### Option 3: AWS Deployment

```bash
# Configure AWS CLI
aws configure

# Run deployment script
bash deployment/deploy.sh characterforge-stack us-east-1

# Get outputs
aws cloudformation describe-stacks \
  --stack-name characterforge-stack \
  --query 'Stacks[0].Outputs'
```

## 📦 Installation

### Requirements

- Python 3.11+
- PostgreSQL 15+ (for production)
- Redis 7+ (for caching)
- Docker & Docker Compose (for containerized deployment)

### Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `streamlit` - Frontend
- `fastapi` - Backend API
- `groq` - LLM provider
- `sqlalchemy` - ORM for SQLite and relational storage
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL adapter
- `redis` - Caching
- `diffusers` - Image generation
- `peft` - LoRA fine-tuning
- `streamlit-authenticator` - Authentication

## 🔐 Authentication

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "kael_warrior",
    "email": "kael@example.com",
    "password": "SecurePass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "kael_warrior",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 🎨 Using Advanced Image Generation

### SDXL + ControlNet

```python
from services.advanced_image_service import generate_sdxl_with_controlnet

image_path = generate_sdxl_with_controlnet(
    prompt="Dark elf warrior with silver eyes",
    character_name="Kael",
    enable_face_restoration=True,
    enable_upscaling=True
)
```

### LoRA Fine-Tuning

```python
from services.advanced_image_service import train_lora_model

model_path = train_lora_model(
    dataset_path="training_data/kael_images/",
    character_name="kael",
    num_epochs=100,
    learning_rate=1e-4
)
```

## 📊 Analytics & Monitoring

### Get Analytics

```bash
curl -X GET http://localhost:8000/api/analytics \
  -H "Authorization: Bearer {token}"
```

### Database Monitoring

```bash
# Connect to PostgreSQL
psql postgresql://user:password@localhost:5432/characterforge

# Check character count
SELECT COUNT(*) FROM characters;

# View analytics
SELECT event_type, COUNT(*) as count FROM analytics 
GROUP BY event_type;
```

### Redis Monitoring

```bash
# Connect to Redis
redis-cli

# Check memory usage
INFO memory

# Monitor cache hits
MONITOR

# Clear cache (if needed)
FLUSHALL
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Characters
- `POST /api/characters` - Create character
- `GET /api/characters` - List user characters
- `GET /api/characters/{id}` - Get character details
- `PUT /api/characters/{id}` - Update character
- `DELETE /api/characters/{id}` - Delete character

### Versioning
- `GET /api/characters/{id}/versions` - Get versions
- `GET /api/characters/{id}/versions/{version}` - Get specific version
- `POST /api/characters/{id}/versions` - Create version

### Relationships
- `POST /api/characters/{id}/relationships` - Add relationship
- `GET /api/characters/{id}/relationships` - Get relationships
- `DELETE /api/relationships/{id}` - Delete relationship

### Lore
- `POST /api/characters/{id}/lore` - Add lore entry
- `GET /api/characters/{id}/lore` - Get lore
- `DELETE /api/lore/{id}` - Delete lore entry

### Search
- `POST /api/search` - Search characters

### Analytics
- `GET /api/analytics` - Get analytics data

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **Test** - Run pytest with coverage
2. **Lint** - Check code quality with flake8, black, isort
3. **Build** - Create Docker image
4. **Security** - Scan with Trivy
5. **Deploy** - Push to ECR and deploy to AWS

Configuration: `.github/workflows/deploy.yml`

## ☁️ AWS Architecture

The deployment creates:

- **EC2**: Application servers (t3.xlarge)
- **RDS**: PostgreSQL database with automated backups
- **ElastiCache**: Redis cluster for caching
- **S3**: Asset storage with versioning
- **CloudFront**: CDN for static assets
- **IAM**: Proper permissions and roles
- **VPC**: Isolated network environment

## 🎓 Learning Resources

- [Streamlit Docs](https://docs.streamlit.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Groq API](https://console.groq.com/docs)
- [SQLite](https://www.sqlite.org/docs.html)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Redis](https://redis.io/docs/)
- [Diffusers](https://huggingface.co/docs/diffusers)
- [PEFT](https://github.com/huggingface/peft)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Groq for LLM API
- Hugging Face for diffusion models
- Streamlit team for the framework
- FastAPI creators
- Open source community

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: preethiregina22prof@gmail.com

---

**Made by 🎭 by Preethi Regina Sundaram Dayalan**

**Current Version**: 2.0.0 | **Last Updated**: 2026-06-06
