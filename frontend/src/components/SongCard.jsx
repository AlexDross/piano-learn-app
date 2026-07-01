import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL

const DIFFICULTY_COLORS = {
  beginner: '#4ade80',
  easy: '#60a5fa',
  intermediate: '#f59e0b',
  hard: '#f87171',
}

function formatDuration(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

export default function SongCard({ song, onFavoriteChange }) {
  const navigate = useNavigate()
  const [fav, setFav] = useState(song.is_favorite)

  const thumbUrl = song.youtube_video_id
    ? `https://img.youtube.com/vi/${song.youtube_video_id}/mqdefault.jpg`
    : null

  async function toggleFavorite(e) {
    e.stopPropagation()
    const next = !fav
    setFav(next)
    await fetch(`${API}/songs/${song.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_favorite: next }),
    })
    onFavoriteChange?.(song.id, next)
  }

  return (
    <div className="song-card" onClick={() => navigate(`/song/${song.id}`)}>
      <div className="song-thumb">
        {thumbUrl ? (
          <img src={thumbUrl} alt="" className="song-thumb-img" />
        ) : (
          <div className="song-thumb-placeholder">🎵</div>
        )}
        <span
          className="difficulty-badge song-thumb-badge"
          style={{ backgroundColor: DIFFICULTY_COLORS[song.difficulty] }}
        >
          {song.difficulty}
        </span>
      </div>

      <div className="song-card-body">
        <button
          className={`fav-btn ${fav ? 'fav-btn-on' : ''}`}
          onClick={toggleFavorite}
          aria-label={fav ? 'Remove from favorites' : 'Add to favorites'}
        >
          ★
        </button>
        <h3 className="song-title">{song.title}</h3>
        <p className="song-artist">{song.artist}</p>
        <div className="song-meta">
          <span className="song-genre">{song.genre}</span>
          <span className="song-duration">{formatDuration(song.duration_sec)}</span>
        </div>
      </div>
    </div>
  )
}
