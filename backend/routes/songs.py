import os
import re
import ssl
import json as _json
import logging
import urllib.parse
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
from models import Song, Difficulty, SourceType, HandMode
from database import get_db

logger = logging.getLogger("uvicorn.error")

# YouTube's own site blocks datacenter IPs (yt-dlp gets "confirm you're not a
# bot"), so we use the official Data API v3, which is built for server-to-server
# access and is not IP-blocked. Requires a free API key set via env var.
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# certifi gives a CA bundle that works on both macOS (whose framework Python
# ships no certs) and Linux, so the HTTPS call succeeds in every environment.
try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover - certifi should be installed
    _SSL_CONTEXT = ssl.create_default_context()

_ISO8601_DURATION = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def _iso8601_to_seconds(iso: str) -> int:
    """Convert an ISO-8601 duration like 'PT6M16S' to total seconds."""
    m = _ISO8601_DURATION.fullmatch(iso or "")
    if not m:
        return 0
    hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
    return hours * 3600 + minutes * 60 + seconds


def fetch_yt_duration(video_id: str) -> int:
    """Return video duration in seconds via the YouTube Data API v3, or 0."""
    if not YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY not set; cannot fetch duration for %s", video_id)
        return 0
    params = urllib.parse.urlencode(
        {"part": "contentDetails", "id": video_id, "key": YOUTUBE_API_KEY}
    )
    url = f"https://www.googleapis.com/youtube/v3/videos?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15, context=_SSL_CONTEXT) as resp:
            data = _json.loads(resp.read().decode())
        items = data.get("items", [])
        if not items:
            logger.warning("YouTube Data API returned no items for %s", video_id)
            return 0
        iso = items[0].get("contentDetails", {}).get("duration", "")
        seconds = _iso8601_to_seconds(iso)
        if seconds == 0:
            logger.warning("Could not parse duration %r for %s", iso, video_id)
        return seconds
    except Exception as e:
        logger.warning("YouTube Data API duration fetch failed for %s: %s", video_id, e)
        return 0


router = APIRouter(prefix="/songs", tags=["songs"])


class SongCreate(BaseModel):
    title: str
    artist: str
    difficulty: Difficulty
    duration_sec: int = 0
    source_type: SourceType = SourceType.youtube
    midi_file_path: Optional[str] = None
    youtube_video_id: Optional[str] = None
    hand_mode: HandMode = HandMode.both
    genre: str
    note_data_json: Optional[str] = None
    is_favorite: bool = False

    @field_validator('title', 'artist', 'genre')
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('must not be blank')
        return v.strip()

    @field_validator('youtube_video_id')
    @classmethod
    def video_id_required_for_youtube(cls, v, info):
        source = info.data.get('source_type')
        if source == SourceType.youtube and not v:
            raise ValueError('youtube_video_id is required for YouTube songs')
        return v


class SongOut(SongCreate):
    id: int

    class Config:
        from_attributes = True


class SongPatch(BaseModel):
    difficulty: Optional[Difficulty] = None
    is_favorite: Optional[bool] = None
    duration_sec: Optional[int] = None


@router.get("/", response_model=list[SongOut])
def list_songs(
    difficulty: Optional[Difficulty] = None,
    genre: Optional[str] = None,
    favorites: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Song)
    if difficulty:
        query = query.filter(Song.difficulty == difficulty)
    if genre:
        query = query.filter(Song.genre == genre)
    if favorites:
        query = query.filter(Song.is_favorite == True)
    return query.all()


@router.get("/{song_id}", response_model=SongOut)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.post("/", response_model=SongOut, status_code=201)
def create_song(song_data: SongCreate, db: Session = Depends(get_db)):
    data = song_data.model_dump()
    if data['source_type'] == SourceType.youtube and data.get('youtube_video_id') and data['duration_sec'] == 0:
        data['duration_sec'] = fetch_yt_duration(data['youtube_video_id'])
    song = Song(**data)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.patch("/{song_id}", response_model=SongOut)
def patch_song(song_id: int, patch: SongPatch, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if patch.difficulty is not None:
        song.difficulty = patch.difficulty
    if patch.is_favorite is not None:
        song.is_favorite = patch.is_favorite
    if patch.duration_sec is not None:
        song.duration_sec = patch.duration_sec
    db.commit()
    db.refresh(song)
    return song
