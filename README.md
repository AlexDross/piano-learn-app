# Piano Learn App

Synthesia-style piano tutorial app for beginners. Browse a song library and learn by watching falling-notes visualizations synced with audio.

## Tech Stack

- **Frontend**: React + Vite (port 5173)
- **Backend**: FastAPI + SQLAlchemy (port 8000)
- **Database**: SQLite (`backend/data/piano_app.db`)

## Running Locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy
uvicorn main:app --reload
```

API available at http://localhost:8000  
Interactive docs at http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at http://localhost:5173

## Project Structure

```
piano-learn-app/
├── frontend/          # React + Vite
│   └── src/
│       ├── components/
│       │   ├── SongLibrary.jsx    # Library grid with filters
│       │   ├── SongCard.jsx       # Individual song card
│       │   ├── FallingNotes.jsx   # Stub — MIDI visualizer (next phase)
│       │   └── YoutubeEmbed.jsx   # Stub — YouTube player (next phase)
│       └── pages/
│           ├── LibraryPage.jsx    # / route
│           └── SongDetailPage.jsx # /song/:id route
├── backend/           # FastAPI
│   ├── main.py        # App entry point + CORS + seeding
│   ├── models.py      # SQLAlchemy Song model
│   ├── database.py    # DB engine + session
│   ├── seed.py        # 3 sample songs
│   ├── routes/
│   │   └── songs.py   # GET /songs, GET /songs/:id, POST /songs
│   └── data/
│       └── piano_app.db
└── scripts/           # Content pipeline scripts (future)
```
