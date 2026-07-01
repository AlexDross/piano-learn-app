import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import FallingNotes from '../components/FallingNotes'
import YoutubeEmbed from '../components/YoutubeEmbed'

const API = import.meta.env.VITE_API_URL

const DIFFICULTIES = ['beginner', 'easy', 'intermediate', 'hard']
const DIFFICULTY_COLORS = {
  beginner: '#4ade80',
  easy: '#60a5fa',
  intermediate: '#f59e0b',
  hard: '#f87171',
}

export default function SongDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [song, setSong] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)
  const toastTimer = useRef(null)

  useEffect(() => {
    fetch(`${API}/songs/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error('Song not found')
        return r.json()
      })
      .then((data) => { setSong(data); setLoading(false) })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [id])

  async function patch(fields) {
    const res = await fetch(`${API}/songs/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fields),
    })
    if (res.ok) {
      clearTimeout(toastTimer.current)
      setSaved(true)
      toastTimer.current = setTimeout(() => setSaved(false), 2000)
    }
  }

  function handleDifficultyChange(e) {
    const newDifficulty = e.target.value
    setSong(s => ({ ...s, difficulty: newDifficulty }))
    patch({ difficulty: newDifficulty })
  }

  function toggleFavorite() {
    const next = !song.is_favorite
    setSong(s => ({ ...s, is_favorite: next }))
    patch({ is_favorite: next })
  }

  if (loading) return <p className="status-msg">Loading…</p>
  if (error) return <p className="status-msg error">{error}</p>

  const color = DIFFICULTY_COLORS[song.difficulty]

  return (
    <div className="page song-detail">
      <button className="back-btn" onClick={() => navigate('/')}>← Back to Library</button>
      <h2>
        {song.title}
        <button
          className={`fav-btn fav-btn-detail ${song.is_favorite ? 'fav-btn-on' : ''}`}
          onClick={toggleFavorite}
          aria-label={song.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          ★
        </button>
      </h2>
      <p className="song-artist">{song.artist}</p>
      <div className="song-detail-meta">
        <div className="difficulty-select-wrap" style={{ '--diff-color': color }}>
          <select
            className="difficulty-select"
            value={song.difficulty}
            onChange={handleDifficultyChange}
          >
            {DIFFICULTIES.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          {saved && <span className="diff-saved">✓ saved</span>}
        </div>
        <span>{song.genre}</span>
      </div>

      <div className="player-area">
        {song.source_type === 'youtube' ? (
          <YoutubeEmbed videoId={song.youtube_video_id} />
        ) : (
          <FallingNotes song={song} />
        )}
      </div>
    </div>
  )
}
