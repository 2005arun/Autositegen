# AutoSiteGen

AutoSiteGen is an AI website builder that turns a natural-language prompt into a built React/Vite/Tailwind application. The original CLI remains available, while the web experience runs through a FastAPI backend and React dashboard.

## Web application

Start the backend from `backend/`:

```powershell
uvicorn main:app --reload --port 8000
```

Start the frontend from `frontend/` in a second terminal:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Set `GROQ_API_KEY` in the repository `.env` before generating websites. The frontend uses `VITE_API_URL` when provided and otherwise targets `http://localhost:8000`.

The web workflow is:

```text
Prompt -> Planner -> Architect -> Coder -> Validator -> Build -> Isolated iframe preview
```

Validation retries are bounded at three attempts. Generated projects are stored in `generated-sites/`, and the API exposes project history, generated files, ZIP downloads, and built preview assets.

## Existing CLI

The original workflow still works from the repository root:

```powershell
python main.py "create a simple portfolio website"
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the agent responsibilities and blueprint categories.
