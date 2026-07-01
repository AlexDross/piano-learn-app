#!/usr/bin/env python3
"""Generate ode_to_joy.mid — 2-hand Ode to Joy for stress-testing the FallingNotes renderer."""
import os
import mido

TEMPO = 500000   # 120 BPM
TPB   = 96

def T(beats):
    return int(round(beats * TPB))

events = []

def on(start, ch, note, vel):
    events.append((T(start), mido.Message('note_on',  channel=ch, note=note, velocity=vel, time=0)))

def off(end, ch, note):
    events.append((T(end),   mido.Message('note_off', channel=ch, note=note, velocity=0,  time=0)))

def melody(start, dur, note, vel=82):
    on(start, 0, note, vel)
    off(start + dur * 0.90, 0, note)

def chord(start, dur, notes, vel=58):
    for n in notes:
        on(start, 1, n, vel)
        off(start + dur * 0.85, 1, n)

# ── Right hand melody ──────────────────────────────────────────────
# All within C3–C6 range (48–84). Key: C major.
# Melody notes: C4=60, D4=62, E4=64, F4=65, G4=67, A4=69

# Phrase 1 (beats 0–15): classic Ode to Joy
for s, d, n in [
    (0, 1, 64), (1, 1, 64), (2, 1, 65), (3, 1, 67),
    (4, 1, 67), (5, 1, 65), (6, 1, 64), (7, 1, 62),
    (8, 1, 60), (9, 1, 60), (10, 1, 62), (11, 1, 64),
    (12, 1.5, 64), (13.5, 0.5, 62), (14, 2, 62),
]:
    melody(s, d, n)

# Phrase 2 (beats 16–31): repeat with lighter touch
for s, d, n in [
    (16, 1, 64), (17, 1, 64), (18, 1, 65), (19, 1, 67),
    (20, 1, 67), (21, 1, 65), (22, 1, 64), (23, 1, 62),
    (24, 1, 60), (25, 1, 60), (26, 1, 62), (27, 1, 64),
    (28, 1.5, 62), (29.5, 0.5, 60), (30, 2, 60),
]:
    melody(s, d, n, vel=76)

# Phrase 3 (beats 32–47): variation with faster figurations
for s, d, n in [
    (32, 1, 62), (33, 1, 62), (34, 1, 64), (35, 1, 60),
    (36, 1, 62), (37, 0.5, 64), (37.5, 0.5, 65), (38, 1, 64), (39, 1, 60),
    (40, 1, 62), (41, 0.5, 64), (41.5, 0.5, 65), (42, 1, 64), (43, 1, 62),
    (44, 1, 60), (45, 1, 62), (46, 2, 55),
]:
    melody(s, d, n)

# Phrase 4 (beats 48–63): return to main theme, louder finish
for s, d, n in [
    (48, 1, 64), (49, 1, 64), (50, 1, 65), (51, 1, 67),
    (52, 1, 67), (53, 1, 65), (54, 1, 64), (55, 1, 62),
    (56, 1, 60), (57, 1, 60), (58, 1, 62), (59, 1, 64),
    (60, 1.5, 62), (61.5, 0.5, 60), (62, 2, 60),
]:
    melody(s, d, n, vel=88)

# ── Left hand chords ───────────────────────────────────────────────
# Voicings all within C3(48)–B3(59) to avoid collision with melody region.
# C major:  C3-E3-G3  = [48, 52, 55]
# G (2nd):  D3-G3-B3  = [50, 55, 59]
# F major:  F3-A3-C4  = [53, 57, 60]  (C4 adds density — intentional stress)
# Am (1st): C3-E3-A3  = [48, 52, 57]

C = [48, 52, 55]
G = [50, 55, 59]
F = [53, 57, 60]
Am= [48, 52, 57]

for s, d, notes in [
    # Phrase 1
    (0,  4, C), (4,  4, G), (8,  4, C), (12, 4, G),
    # Phrase 2
    (16, 4, C), (20, 4, G), (24, 4, C), (28, 4, G),
    # Phrase 3 — more movement, 2-beat changes
    (32, 2, F), (34, 2, C), (36, 2, F), (38, 2, C),
    (40, 2, F), (42, 2, Am),(44, 2, G), (46, 2, C),
    # Phrase 4
    (48, 4, C), (52, 4, G), (56, 4, C), (60, 2, G), (62, 2, C),
]:
    chord(s, d, notes)

# ── Build MIDI ─────────────────────────────────────────────────────
events.sort(key=lambda e: e[0])

mid   = mido.MidiFile(ticks_per_beat=TPB)
track = mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.MetaMessage('set_tempo', tempo=TEMPO, time=0))
track.append(mido.MetaMessage('track_name', name='Ode to Joy', time=0))

prev = 0
for abs_tick, msg in events:
    delta = abs_tick - prev
    track.append(msg.copy(time=delta))
    prev = abs_tick

out_dir  = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'midi_files')
out_path = os.path.join(out_dir, 'ode_to_joy.mid')
os.makedirs(out_dir, exist_ok=True)
mid.save(out_path)
print(f"Saved: {os.path.abspath(out_path)}")
print(f"Total events: {len(events)}, duration: ~{64 * 0.5:.0f}s")
