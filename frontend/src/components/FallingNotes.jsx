import { useEffect, useRef, useState, useCallback } from 'react'
import { Midi } from '@tonejs/midi'
import * as Tone from 'tone'

const API_BASE        = import.meta.env.VITE_API_URL
const LOOK_AHEAD_SECS = 4
const CANVAS_HEIGHT   = 540
const KEYBOARD_HEIGHT = 130
const MIN_MIDI        = 48    // C3
const MAX_MIDI        = 84    // C6
const BLACK_SEMITONES = new Set([1, 3, 6, 8, 10])
const BASE_BPM        = 120   // matches our MIDI files' tempo
const SPEEDS          = [0.5, 0.75, 1.0, 1.25]

const NOTE_COLORS = [
  '#a78bfa', '#60a5fa', '#34d399', '#fbbf24',
  '#f87171', '#e879f9', '#38bdf8', '#fb923c',
]

function isBlack(n) { return BLACK_SEMITONES.has(n % 12) }

function buildLayout(canvasW) {
  let whiteCount = 0
  for (let n = MIN_MIDI; n <= MAX_MIDI; n++) {
    if (!isBlack(n)) whiteCount++
  }
  const wkW = canvasW / whiteCount
  const bkW = wkW * 0.6
  const layout = {}
  let wi = 0
  for (let n = MIN_MIDI; n <= MAX_MIDI; n++) {
    if (!isBlack(n)) {
      layout[n] = { x: wi * wkW, w: wkW, isBlack: false }
      wi++
    } else {
      layout[n] = { x: wi * wkW - bkW / 2, w: bkW, isBlack: true }
    }
  }
  return { layout, wkW, bkW }
}

export default function FallingNotes({ song }) {
  const wrapperRef = useRef(null)
  const canvasRef  = useRef(null)
  const rafRef     = useRef(null)
  const synthRef   = useRef(null)
  const partRef    = useRef(null)
  const notesRef   = useRef([])
  const layoutRef  = useRef(null)

  // Song-position accumulator — tracks Σ(Δt × speed) independently of Transport.seconds
  // because Transport.seconds is real-clock time regardless of BPM.
  const songPosRef  = useRef(0)
  const lastTRef    = useRef(0)
  const playingRef  = useRef(false)

  const [status, setStatus]       = useState('loading')
  const [errorMsg, setErrorMsg]   = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed]         = useState(1.0)

  const midiUrl = song?.midi_file_path
    ? `${API_BASE}/static/${song.midi_file_path}`
    : null

  // ── 1. Load MIDI + create Tone objects ──────────────────────────
  useEffect(() => {
    if (!midiUrl) { setErrorMsg('No MIDI file path for this song.'); setStatus('error'); return }
    let cancelled = false

    fetch(midiUrl)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status} — MIDI not found: ${midiUrl}`)
        return r.arrayBuffer()
      })
      .then(buf => {
        if (cancelled) return
        const midi = new Midi(buf)
        const notes = []
        midi.tracks.forEach(track => {
          track.notes.forEach(note => {
            notes.push({
              midi: note.midi, time: note.time,
              duration: note.duration, velocity: note.velocity,
              colorIdx: note.midi % NOTE_COLORS.length,
            })
          })
        })
        notes.sort((a, b) => a.time - b.time)
        notesRef.current = notes

        Tone.Transport.bpm.value = BASE_BPM

        synthRef.current = new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: 'triangle' },
          envelope:   { attack: 0.01, decay: 0.08, sustain: 0.55, release: 0.5 },
          volume: -10,
        }).toDestination()

        partRef.current = new Tone.Part((time, n) => {
          synthRef.current.triggerAttackRelease(
            Tone.Frequency(n.midi, 'midi').toFrequency(),
            n.duration, time, n.velocity,
          )
        }, notes)
        partRef.current.start(0)

        setStatus('ready')
      })
      .catch(e => { if (!cancelled) { setErrorMsg(e.message); setStatus('error') } })

    return () => {
      cancelled = true
      Tone.Transport.stop()
      Tone.Transport.cancel()
      partRef.current?.dispose()
      synthRef.current?.dispose()
    }
  }, [midiUrl])

  // ── 2. Sync BPM to speed (pitch-correct via Transport tick scaling) ──
  // Tone schedules Part events as ticks (computed at BPM=120 at load time).
  // Changing BPM changes how fast ticks fire → slows/speeds audio without pitch shift.
  useEffect(() => {
    if (status !== 'ready') return
    Tone.Transport.bpm.value = BASE_BPM * speed
  }, [speed, status])

  // ── 3. Canvas + animation loop ───────────────────────────────────
  useEffect(() => {
    if (status !== 'ready') return

    const canvas  = canvasRef.current
    const wrapper = wrapperRef.current
    const ctx     = canvas.getContext('2d')
    canvas.height = CANVAS_HEIGHT

    function resize() {
      const w = Math.floor(wrapper.clientWidth)
      if (canvas.width === w) return
      canvas.width      = w
      layoutRef.current = buildLayout(w)
    }
    resize()
    const ro = new ResizeObserver(resize)
    ro.observe(wrapper)

    // Draw helpers — all read from refs, none capture speed/layout as closures
    function drawBackground(W, notesH) {
      ctx.fillStyle = '#0c0c14'
      ctx.fillRect(0, 0, W, CANVAS_HEIGHT)
      const { layout } = layoutRef.current
      ctx.strokeStyle = '#1c1c28'; ctx.lineWidth = 1
      for (let n = MIN_MIDI; n <= MAX_MIDI; n++) {
        if (isBlack(n)) continue
        const k = layout[n]
        ctx.beginPath(); ctx.moveTo(k.x, 0); ctx.lineTo(k.x, notesH); ctx.stroke()
      }
      ctx.strokeStyle = '#1a1a26'; ctx.lineWidth = 0.5
      for (let s = 1; s < LOOK_AHEAD_SECS; s++) {
        const y = notesH * (1 - s / LOOK_AHEAD_SECS)
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }
    }

    function drawFallingNotes(songTime, notesH, pxPerSec) {
      const { layout } = layoutRef.current
      notesRef.current.forEach(note => {
        const k = layout[note.midi]
        if (!k) return
        const ttl     = note.time - songTime
        const noteEnd = note.time + note.duration
        if (ttl > LOOK_AHEAD_SECS) return
        if (noteEnd < songTime - 0.05) return

        const barBottom = notesH - ttl * pxPerSec
        const barH      = Math.max(note.duration * pxPerSec, 5)
        const barTop    = barBottom - barH
        const drawTop   = Math.max(0, barTop)
        const drawBot   = Math.min(notesH, barBottom)
        if (drawBot <= drawTop) return

        const color = NOTE_COLORS[note.colorIdx]
        const pad = 1.5
        const x = k.x + pad, w = k.w - pad * 2

        const sounding = songTime >= note.time && songTime < noteEnd
        if (sounding) { ctx.shadowColor = color; ctx.shadowBlur = 14 }

        ctx.fillStyle   = color
        ctx.globalAlpha = k.isBlack ? 0.95 : 0.87
        ctx.beginPath()
        const r = Math.min(4, w / 3)
        ctx.roundRect(x, drawTop, w, drawBot - drawTop, barTop >= 0 ? [r, r, 0, 0] : 0)
        ctx.fill()

        if (sounding) ctx.shadowBlur = 0
        ctx.globalAlpha = 1
      })
    }

    function drawKeyboard(activeSet, notesH, wkW) {
      const { layout } = layoutRef.current
      const BKH = KEYBOARD_HEIGHT * 0.64
      for (let n = MIN_MIDI; n <= MAX_MIDI; n++) {
        if (isBlack(n)) continue
        const k = layout[n]; const active = activeSet.has(n)
        ctx.fillStyle = active ? '#c4b5fd' : '#eeeaf6'
        ctx.strokeStyle = '#4a4a5a'; ctx.lineWidth = 0.8
        ctx.fillRect(  k.x + 0.5, notesH, k.w - 1, KEYBOARD_HEIGHT - 1)
        ctx.strokeRect(k.x + 0.5, notesH, k.w - 1, KEYBOARD_HEIGHT - 1)
        if (n % 12 === 0) {
          ctx.fillStyle = active ? '#5b21b6' : '#aaa'
          ctx.font = `${Math.max(8, wkW * 0.38)}px sans-serif`; ctx.textAlign = 'center'
          ctx.fillText(`C${Math.floor(n / 12) - 1}`, k.x + k.w / 2, notesH + KEYBOARD_HEIGHT - 8)
        }
      }
      for (let n = MIN_MIDI; n <= MAX_MIDI; n++) {
        if (!isBlack(n)) continue
        const k = layout[n]; const active = activeSet.has(n)
        ctx.fillStyle = active ? '#7c3aed' : '#111120'
        ctx.fillRect(k.x, notesH, k.w, BKH)
        if (active) { ctx.strokeStyle = '#a78bfa'; ctx.lineWidth = 1; ctx.strokeRect(k.x, notesH, k.w, BKH) }
      }
    }

    function frame() {
      if (!layoutRef.current) { rafRef.current = requestAnimationFrame(frame); return }

      // Accumulate song position: Σ(Δ Transport.seconds × speed)
      // This stays correct even when speed changes mid-song because each delta
      // is multiplied by the speed that was active during that interval.
      const currentT = Tone.Transport.seconds
      const delta    = Math.max(0, currentT - lastTRef.current)
      lastTRef.current = currentT
      if (playingRef.current) {
        // Use live BPM ratio rather than a stale speed closure
        songPosRef.current += delta * (Tone.Transport.bpm.value / BASE_BPM)
      }
      const songTime = songPosRef.current

      const W       = canvas.width
      const notesH  = CANVAS_HEIGHT - KEYBOARD_HEIGHT
      const pxPerSec = notesH / LOOK_AHEAD_SECS
      const { wkW } = layoutRef.current

      drawBackground(W, notesH)

      const activeSet = new Set()
      notesRef.current.forEach(n => {
        if (songTime >= n.time && songTime < n.time + n.duration) activeSet.add(n.midi)
      })

      drawFallingNotes(songTime, notesH, pxPerSec)
      drawKeyboard(activeSet, notesH, wkW)

      rafRef.current = requestAnimationFrame(frame)
    }

    frame()
    return () => { ro.disconnect(); cancelAnimationFrame(rafRef.current) }
  }, [status])

  // ── Controls ─────────────────────────────────────────────────────
  const togglePlay = useCallback(async () => {
    await Tone.start()
    if (playingRef.current) {
      Tone.Transport.pause()
      playingRef.current = false
      setIsPlaying(false)
    } else {
      // Reset lastT so paused time isn't counted as song progress
      lastTRef.current = Tone.Transport.seconds
      Tone.Transport.start()
      playingRef.current = true
      setIsPlaying(true)
    }
  }, [])

  const restart = useCallback(async () => {
    await Tone.start()
    Tone.Transport.stop()
    songPosRef.current = 0
    lastTRef.current   = 0
    Tone.Transport.bpm.value = BASE_BPM * speed
    Tone.Transport.start()
    playingRef.current = true
    setIsPlaying(true)
  }, [speed])

  const changeSpeed = useCallback((s) => {
    setSpeed(s)
    // BPM update handled by the speed useEffect; no need to reschedule Part
  }, [])

  if (status === 'loading') return <div className="stub-placeholder"><p>Loading MIDI…</p></div>
  if (status === 'error')   return <div className="stub-placeholder"><p>Error: {errorMsg}</p></div>

  return (
    <div className="falling-notes-wrapper" ref={wrapperRef}>
      <canvas ref={canvasRef} className="falling-notes-canvas" />
      <div className="falling-notes-controls">
        <button className="play-btn"    onClick={togglePlay}>{isPlaying ? '⏸ Pause' : '▶ Play'}</button>
        <button className="restart-btn" onClick={restart}>⟳ Restart</button>
        <div className="speed-chips">
          {SPEEDS.map(s => (
            <button
              key={s}
              className={`chip speed-chip ${speed === s ? 'chip-active' : ''}`}
              onClick={() => changeSpeed(s)}
            >
              {s}×
            </button>
          ))}
        </div>
        <span className="transport-label">{song?.title ?? 'MIDI'}</span>
      </div>
    </div>
  )
}
