import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
from models import Base
from routes.songs import router as songs_router
from seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(5):
        try:
            Base.metadata.create_all(bind=engine)
            seed()
            break
        except Exception as e:
            if attempt == 4:
                raise
            print(f"DB startup attempt {attempt+1} failed: {e}. Retrying in 5s...")
            time.sleep(5)
    yield


app = FastAPI(title="Piano Learn API", lifespan=lifespan)

_default_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
]
_cors_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs_router)

_data_dir = os.path.join(os.path.dirname(__file__), "data")
if os.path.isdir(_data_dir):
    app.mount("/static", StaticFiles(directory=_data_dir), name="static")


@app.get("/")
def root():
    return {"status": "ok"}
