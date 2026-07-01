import { useState } from 'react'

const API = import.meta.env.VITE_API_URL
const DIFFICULTIES = ['beginner', 'easy', 'intermediate', 'hard']

function extractVideoId(url) {
  url = url.trim()
  // youtu.be/VIDEO_ID
  const short = url.match(/youtu\.be\/([A-Za-z0-9_-]{11})/)
  if (short) return short[1]
  // youtube.com/watch?v=VIDEO_ID
  const long = url.match(/[?&]v=([A-Za-z0-9_-]{11})/)
  if (long) return long[1]
  // bare 11-char ID pasted directly
  if (/^[A-Za-z0-9_-]{11}$/.test(url)) return url
  return null
}

const EMPTY = { youtubeUrl: '', title: '', artist: '', difficulty: 'easy', genre: '' }

export default function AddSongPage() {
  const [form, setForm] = useState(EMPTY)
  const [videoId, setVideoId] = useState(null)
  const [urlError, setUrlError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  function handleUrlChange(e) {
    const raw = e.target.value
    setForm(f => ({ ...f, youtubeUrl: raw }))
    if (!raw.trim()) { setVideoId(null); setUrlError(''); return }
    const id = extractVideoId(raw)
    if (id) { setVideoId(id); setUrlError('') }
    else { setVideoId(null); setUrlError('Could not extract a video ID from this URL') }
  }

  function handleChange(e) {
    const { name, value } = e.target
    setForm(f => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(''); setSuccess('')

    if (!videoId) { setUrlError('Valid YouTube URL required'); return }

    setSubmitting(true)
    try {
      const res = await fetch(`${API}/songs/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: form.title,
          artist: form.artist,
          difficulty: form.difficulty,
          genre: form.genre,
          source_type: 'youtube',
          youtube_video_id: videoId,
        }),
      })
      if (!res.ok) {
        const body = await res.json()
        throw new Error(body.detail?.[0]?.msg ?? body.detail ?? 'Server error')
      }
      const song = await res.json()
      setSuccess(`Added "${song.title}" by ${song.artist} (id ${song.id})`)
      setForm(EMPTY)
      setVideoId(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page add-song-page">
      <h2>Add Song</h2>

      <form className="add-song-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="youtubeUrl">YouTube URL</label>
          <input
            id="youtubeUrl"
            name="youtubeUrl"
            type="text"
            placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..."
            value={form.youtubeUrl}
            onChange={handleUrlChange}
            autoComplete="off"
          />
          {urlError && <span className="field-error">{urlError}</span>}
          {videoId && <span className="field-hint">Video ID: {videoId}</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              name="title"
              type="text"
              placeholder="Song title"
              value={form.title}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="artist">Artist</label>
            <input
              id="artist"
              name="artist"
              type="text"
              placeholder="Artist name"
              value={form.artist}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="difficulty">Difficulty</label>
            <select id="difficulty" name="difficulty" value={form.difficulty} onChange={handleChange}>
              {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="genre">Genre</label>
            <input
              id="genre"
              name="genre"
              type="text"
              placeholder="e.g. Pop, Rock, Classical"
              value={form.genre}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        {error && <p className="form-error">{error}</p>}
        {success && <p className="form-success">{success}</p>}

        <button type="submit" className="submit-btn" disabled={submitting}>
          {submitting ? 'Adding…' : 'Add Song'}
        </button>
      </form>
    </div>
  )
}
