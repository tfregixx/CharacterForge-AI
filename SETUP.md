# CharacterForge AI - Setup Guide

## Quick Start (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/tfregixx/CharacterForge-AI.git
cd CharacterForge-AI
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Get Groq API Key
1. Visit [Groq Console](https://console.groq.com)
2. Create account (free)
3. Generate API key
4. Create `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

### Step 5: Run App
```bash
streamlit run app.py
```

Access at `http://localhost:8501`

---

## Advanced Setup

### Development Mode
```bash
pip install -r requirements-dev.txt
```

### Docker Setup
```bash
# Build image
docker build -t characterforge .

# Run container
docker run -p 8501:8501 -e GROQ_API_KEY=your_key characterforge
```

### Cloud Deployment

#### Streamlit Community Cloud
1. Push repository to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect GitHub account
4. Select `CharacterForge-AI` repository
5. Add `GROQ_API_KEY` in Secrets
6. Deploy!

#### Alternative: Heroku (if using wsgi server)
```bash
heroku login
heroku create characterforge-app
git push heroku main
heroku config:set GROQ_API_KEY=your_key
```

---

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Memory Issues (Image Generation)
- Image generation requires ~6GB GPU memory
- Use CPU-only: Edit `image_generator.py` and remove `torch.float16`
- Or skip image generation and use placeholder

### Database Issues
```bash
# Reset database
rm characters.db
python -c "from database.db import *"
```

### API Errors
- Verify API key in `.env`
- Check Groq dashboard for rate limits
- Ensure internet connection

---

## File Structure

```
app.py                      Main application
requirements.txt            Dependencies
.env                       Secrets (git ignored)
.streamlit/config.toml     Streamlit configuration

services/
  ├── character_generator.py
  ├── chat_service.py
  ├── memory_service.py
  ├── image_generator.py
  └── export_service.py

database/
  └── db.py

data/                       Data storage
assets/                     Static files
exports/                    Export output
```

---

## Feature Guide

### 1. Character Generation
- Select genre and type
- Add custom details (optional)
- AI generates unique character
- Save to database

### 2. Character Chat
- Select any character
- Chat in real-time
- Character maintains personality
- Conversations are remembered

### 3. Image Generation
- AI generates character portrait
- Saved automatically
- Can be regenerated

### 4. Export Characters
- JSON: Portable data format
- TXT: Human-readable card
- PDF: Professional sheet

---

## Performance Tips

1. **Local Development**: Use SQLite (default)
2. **Production**: Consider PostgreSQL
3. **Image Generation**: Cache generated images
4. **Chat**: Limit memory retrieval to 5 most relevant
5. **Database**: Add indexes for frequent queries

---

## Security

1. Never commit `.env` file
2. Use strong API keys
3. Validate user inputs
4. Run in isolated container
5. Use HTTPS in production

---

## Next Steps

1. Generate your first character
2. Save it to database
3. Chat with your character
4. Export your character
5. Deploy to Streamlit Cloud

Enjoy! 🎭
