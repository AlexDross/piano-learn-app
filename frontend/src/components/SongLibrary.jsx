import { useState, useEffect } from 'react'
import SongCard from './SongCard'

const API = import.meta.env.VITE_API_URL

const DIFFICULTIES = ['beginner', 'easy', 'intermediate', 'hard']

export default function SongLibrary({ favoritesOnly = false }) {
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [difficulty, setDifficulty] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const params = new URLSearchParams()
    if (difficulty) params.set('difficulty', difficulty)
    if (favoritesOnly) params.set('favorites', 'true')

    fetch(`${API}/songs/?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(`Server error ${r.status}`)
        return r.json()
      })
      .then((data) => {
        if (!cancelled) { setSongs(data); setLoading(false) }
      })
      .catch((e) => {
        if (!cancelled) { setSongs([]); setError(e.message); setLoading(false) }
      })

    return () => { cancelled = true }
  }, [difficulty, favoritesOnly])

  // When a card's favorite is toggled off in Favorites view, remove it from the list
  function handleFavoriteChange(id, isFav) {
    if (favoritesOnly && !isFav) {
      setSongs(s => s.filter(song => song.id !== id))
    }
  }

  const emptyMsg = favoritesOnly
    ? 'No favorites yet — star a song to add it here.'
    : 'No songs in this category yet.'

  return (
    <div className="library">
      {!favoritesOnly && (
        <div className="filters">
          <div className="filter-group">
            <span className="filter-label">Difficulty:</span>
            <button
              className={`chip ${!difficulty ? 'chip-active' : ''}`}
              onClick={() => setDifficulty(null)}
            >
              All
            </button>
            {DIFFICULTIES.map((d) => (
              <button
                key={d}
                className={`chip ${difficulty === d ? 'chip-active' : ''}`}
                onClick={() => setDifficulty(difficulty === d ? null : d)}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && <p className="status-msg">Loading songs…</p>}
      {error && <p className="status-msg error">Error: {error}</p>}
      {!loading && !error && songs.length === 0 && (
        <p className="status-msg">{emptyMsg}</p>
      )}

      <div className="song-grid">
        {songs.map((song) => (
          <SongCard key={song.id} song={song} onFavoriteChange={handleFavoriteChange} />
        ))}
      </div>
    </div>
  )
}
