# Quick Start Guide

## Running the Application

### Option 1: Start Everything at Once (Recommended)

```bash
./start.sh
```

This will:
- Check/create your `.env` file
- Install missing dependencies
- Start both backend and frontend
- Show you the URLs to access

### Option 2: Start Services Separately

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

## First Time Setup

1. **Environment Variables**

   The start script will create a `.env` file from `.env.example` if it doesn't exist.

   Edit `.env` and add at least one API key:
   ```bash
   # Required: At least one of these
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   GOOGLE_API_KEY=your-google-key-here
   OLLAMA_BASE_URL=http://localhost:11434  # For local models
   ```

2. **Run the application**
   ```bash
   ./start.sh
   ```

## Accessing the Application

Once running, open your browser to:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)

## Viewing Logs

The start script creates log files in the project root:

```bash
# Watch backend logs
tail -f backend.log

# Watch frontend logs
tail -f frontend.log
```

## Stopping the Application

Press `Ctrl+C` in the terminal where you ran `./start.sh`

This will cleanly shut down both services.

## Manual Installation (if needed)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Troubleshooting

### Port Already in Use

If port 8000 or 5173 is already in use:

1. Stop the conflicting service
2. Or modify the ports in `.env`:
   ```
   PORT=8001  # Backend port
   ```
   And in `frontend/vite.config.ts` for frontend port

### API Connection Errors

1. Ensure backend is running: http://localhost:8000/api/health
2. Check backend logs: `tail -f backend.log`
3. Verify `.env` has valid API keys

### Dependencies Not Installing

**Backend:**
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. Open http://localhost:5173
2. Configure a persona (Actor characteristics)
3. Set your objective (what to test)
4. Select AI providers for Actor and Subject roles
5. Run simulation!

See the main [README.md](README.md) for full documentation.
