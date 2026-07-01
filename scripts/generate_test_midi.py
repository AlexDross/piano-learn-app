#!/usr/bin/env python3
"""Generate test_melody.mid (Twinkle Twinkle Little Star) for the FallingNotes visualizer."""
import os
import mido

TEMPO = 500000   # 120 BPM
TPB   = 96       # ticks per beat

# (midi_note, quarter_note_beats)
MELODY = [
    (60, 1), (60, 1), (67, 1), (67, 1), (69, 1), (69, 1), (67, 2),
    (65, 1), (65, 1), (64, 1), (64, 1), (62, 1), (62, 1), (60, 2),
    (67, 1), (67, 1), (65, 1), (65, 1), (64, 1), (64, 1), (62, 2),
    (67, 1), (67, 1), (65, 1), (65, 1), (64, 1), (64, 1), (62, 2),
    (60, 1), (60, 1), (67, 1), (67, 1), (69, 1), (69, 1), (67, 2),
    (65, 1), (65, 1), (64, 1), (64, 1), (62, 1), (62, 1), (60, 2),
]

def main():
    mid = mido.MidiFile(ticks_per_beat=TPB)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage('set_tempo', tempo=TEMPO, time=0))
    track.append(mido.MetaMessage('track_name', name='Melody', time=0))

    for note, beats in MELODY:
        ticks = int(beats * TPB)
        track.append(mido.Message('note_on',  note=note, velocity=80, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0,  time=ticks))

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'midi_files')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'test_melody.mid')
    mid.save(out_path)
    print(f"Saved: {os.path.abspath(out_path)}")

if __name__ == '__main__':
    main()
