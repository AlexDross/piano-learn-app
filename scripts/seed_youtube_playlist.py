#!/usr/bin/env python3
"""
Seed YouTube playlist songs into the database.
Uses yt-dlp metadata already fetched; manual overrides handle ~10 non-standard titles.
"""
import re
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import Song, Difficulty, SourceType, HandMode

# ── Raw yt-dlp output (id|title|channel|duration) ───────────────────────────
RAW = """\
P3u3hK4KYsE|Harry Styles - Sign Of The Times | EASY Piano Tutorial|NA|376.0
d1D8FNzeLn4|Passenger - Let Her Go | EASY Piano Tutorial|NA|333.0
ESeV0gZ-gS4|The Fray - How To Save a Life (Easy Piano Tutorial)|NA|267.0
crHMq5HZkxk|Gravity ~ John Mayer (piano tutorial)|NA|229.0
KgpKFDFE1XE|Green Day - Wake Me Up When September Ends | EASY Piano Tutorial|NA|201.0
PMQLWfvL3rY|Have You Ever Seen the Rain Easy Piano|NA|217.0
o27h9ihvcJ8|Israel "IZ" Kamakawiwo'ole - Somewhere Over The Rainbow | EASY Piano Tutorial|NA|225.0
iOFZ7_ssO9Y|STEVIE WONDER - I JUST CALLED TO SAY I LOVE YOU | SLOW & EASY PIANO TUTORIAL|NA|386.0
Z_f2T3Zrj-Y|P!nk - Just Give Me A Reason (ft. Nate Ruess) | EASY Piano Tutorial|NA|261.0
m4izR6COXP0|Yesterday - The Beatles | VERY EASY Piano Tutorial|NA|172.0
grku0fnTESY|Goo Goo Dolls - Iris | EASY Piano Tutorial|NA|258.0
_ZvfdI3Aj7A|Mad World - Gary Jules (Tears For Fears) | EASY Piano Tutorial|NA|131.0
LJRfG-QYgII|Phillip Phillips - Home (Easy Piano Tutorial)|NA|217.0
i0sjhlqQql0|Charles Strouse - Tomorrow (from Annie) - Easy Piano Tutorials|NA|147.0
0voHyU27R9c|The Beatles - Here Comes The Sun | EASY Piano Tutorial|NA|188.0
Ek9T05_tZU8|The Beatles - Hey Jude | EASY Piano Tutorial|NA|266.0
jRzzL96LVmg|R.E.M. - Losing My Religion (Easy Piano Tutorial)|NA|276.0
RPaRJvvWiRY|Zach Bryan - Open the Gate (Piano Tutorial)|NA|244.0
JCXJRAD_Dls|Journey - Don't Stop Believin' | EASY Piano Tutorial|NA|240.0
1eEIYbaZxVA|Bon Jovi - Livin' On A Prayer | EASY Piano Tutorial|NA|285.0
A8Ccfn5rSf0|OneRepublic - Counting Stars | EASY Piano Tutorial|NA|308.0
PP_axhKFv9Q|Mötley Crüe - Home Sweet Home - EASY Piano CHORDS TUTORIAL by Piano Fun Play|NA|232.0
dQW3Y3sHCFE|Stevie Wonder - Isn't She Lovely | EASY Piano Tutorial|NA|282.0
5FVlZ7FoyIQ|Ed Sheeran - Thinking Out Loud | EASY Piano Tutorial|NA|281.0
finoJErQu5w|Fleetwood Mac - Dreams | Piano Tutorial|NA|260.0
1i8FuVrto5o|Aerosmith - Dream On - EASY Piano Tutorial|NA|290.0
OYBHdImGQnw|4 Non Blondes - What's Up | EASY Piano Tutorial|NA|150.0
_mSblGTAFZI|ELTON JOHN - YOUR SONG | SLOW & EASY PIANO TUTORIAL|NA|411.0
xkX3N0Txpxk|Queen - The Show Must Go On | EASY Piano Tutorial|NA|299.0
mwFL-r0LBnQ|ABBA - Dancing Queen | EASY Piano Tutorial|NA|170.0
M6k17IvFUhA|Green Day - Boulevard Of Broken Dreams | EASY Piano Tutorial|NA|297.0
6ojcFe0qN_k|Tory Lanez - The Color Violet - Piano Tutorial|NA|291.0
hv2ZNnL3MQ8|Maroon 5 - Won't Go Home Without You | EASY Piano Tutorial ||NA|238.0
is0U3-8T8VQ|JASON MRAZ - I WON'T GIVE UP | SLOW & EASY PIANO TUTORIAL|NA|331.0
mv8qzUelUUY|Bruno Mars - Count On Me | EASY Piano Tutorial|NA|237.0
XQClJkKYHpM|Bruno Mars - Just The Way You Are | EASY Piano Tutorial|NA|181.0
N3U0OMniW7s|GREEN DAY - GOOD RIDDANCE ( TIME OF YOUR LIFE ) | SLOW & EASY PIANO TUTORIAL|NA|248.0
NoxXAZvI-0k|BILLY JOEL - GOODNIGHT SAIGON | SLOW & EASY PIANO TUTORIAL|NA|463.0
spreYrQA26s|THE FOUNDATION - BUILD ME UP BUTTERCUP | SLOW & EASY PIANO TUTORIAL|NA|318.0
-iesgRgi6-E|MICHAEL JACKSON - BEAT IT | SLOW & EASY PIANO TUTORIAL|NA|378.0
A6s_-brGJck|BRUNO MARS ft. TRAVIE MCCOY - BILLIONAIRE | SLOW & EASY PIANO TUTORIAL|NA|355.0
ETbilyzxtp4|VIENNA [ HD ] - BILLY JOEL | EASY PIANO|NA|332.0
37-vJ9RCjn8|BILLY JOEL - SHE'S ALWAYS A WOMAN | SLOW & EASY PIANO TUTORIAL|NA|320.0
OqwTNevdPGo|Pearl Jam - Last Kiss - Easy Piano with Chords|NA|235.0
9QEuMMISh8A|The Beatles - Strawberry Fields Forever - Piano Tutorial + SHEETS|NA|241.0
dVkZM9qNGao|THE BEATLES - WHEN I'M 64 | SLOW & EASY PIANO TUTORIAL|NA|294.0
HLWntfUjKls|Penny Lane (The Beatles) - Easy piano tutorial|NA|160.0
_h1Ygk3ix6w|While My Guitar Gently Weeps - The Beatles Easy Mode|NA|270.0
v_NeKzsclQ0|Red Hot Chili Peppers - Dark Necessities Piano Tutorial | Medium|NA|282.0
yITT5_0RbK8|Zach Bryan - Jake's Piano - Long Island (Piano Tutorial)|NA|314.0
bh1A9uYRKA4|The Beatles - Blackbird | EASY Piano Tutorial|NA|165.0
YzynH_2GzcI|Coldplay - Viva La Vida | EASY Piano Tutorial|NA|279.0
dthwWpuLT-s|The Beatles - Yellow Submarine | EASY Piano Tutorial|NA|179.0
xLJoInqG1gA|The Beatles - In My Life | EASY Piano Tutorial|NA|116.0
6EHIIE_8k6w|A Million Dreams - The Greatest Showman Cast | EASY PIANO TUTORIAL + SHEET MUSIC by Betacustic|NA|234.0
HoqRlSEFM7w|Tones And I - Dance Monkey | EASY Piano Tutorial|NA|231.0
AsDt77IQ5qY|Eminem - Mockingbird | EASY Piano Tutorial|NA|106.0
SGMoa6GMCjc|Led Zeppelin - Stairway To Heaven | SLOW EASY Piano Tutorial|NA|360.0
LAd-euW43so|David Bowie - Life On Mars - EASY Piano Tutorial|NA|243.0
aLv5oIqKfBg|Neil Diamond - Sweet Caroline | EASY Piano Tutorial|NA|266.0
8pi27xfwvnM|Can't Help Falling In Love - Elvis Presley | EASY Piano Tutorial|NA|187.0
OJz5Ezg9Pws|Elton John - Goodbye Yellow Brick Road (SLOW EASY PIANO TUTORIAL)|NA|220.0
CipHPp7cyXk|David Guetta - Titanium ft. Sia | EASY Piano Tutorial|NA|269.0
wo3GOKzQQO4|Hozier - Take Me To Church | EASY Piano Tutorial|NA|274.0
G5Jt1EcuMG4|Lady Gaga, Bradley Cooper - Shallow (Easy Piano Tutorial)|NA|219.0
xJHjpKcnDCg|Bruno Mars - Marry You | EASY Piano Tutorial|NA|275.0
MRXgdxq5hOM|Bruno Mars - Grenade | EASY Piano Tutorial|NA|231.0
lBJyR56qMLI|Bastille - Pompeii (Easy Piano Tutorial)|NA|217.0
_EH_3GbbnMo|Adele - Someone Like You | EASY Piano Tutorial|NA|301.0
Ip4PcspNZBA|The Beatles - All My Loving | EASY Piano Tutorial|NA|140.0
Z_87ye5rCLI|Bruno Mars - When I Was Your Man | EASY Piano Tutorial|NA|209.0
j1cFOSh0v-Q|Bruno Mars - Talking To The Moon | EASY Piano Tutorial|NA|226.0
b0ErLXm8OYo|John Legend - All Of Me | SLOW EASY Piano Tutorial|NA|371.0
UVUoOQL9SeI|Bohemian Rhapsody - Queen [Easy Piano Tutorial] (Synthesia/Sheet Music)|NA|350.0
4uSLE4SZ9YE|Maroon 5 - She Will Be Loved | EASY Piano Tutorial|NA|294.0
bUBbUX7N4Fo|Adele - Set Fire To The Rain | EASY Piano Tutorial|NA|311.0
oqbryIcmueo|Zach Bryan - Something In The Orange (Piano Tutorial)|NA|241.0
SIo9DXT_VJk|Plain White T's - Hey There Delilah | EASY Piano Tutorial|NA|335.0
ZK7NH5YGrAc|Morgan Wallen - Sand In My Boots (Piano Tutorial)|NA|218.0
O3OQqhgS7Vw|Morgan Wallen - Wasted On You (Piano Tutorial)|NA|204.0
JKxrgDJMCWY|Bruno Mars - Locked Out of Heaven (Easy Piano Tutorial)|NA|234.0
"""

# ── Manual overrides: video_id → (artist, clean_title) ──────────────────────
# Used for "Song - Artist" reversals and other non-standard formats.
OVERRIDES = {
    'm4izR6COXP0': ('The Beatles',               'Yesterday'),
    '_ZvfdI3Aj7A': ('Gary Jules',                'Mad World'),
    'ETbilyzxtp4': ('Billy Joel',                'Vienna'),
    '_h1Ygk3ix6w': ('The Beatles',               'While My Guitar Gently Weeps'),
    '6EHIIE_8k6w': ('The Greatest Showman Cast', 'A Million Dreams'),
    '8pi27xfwvnM': ('Elvis Presley',             "Can't Help Falling in Love"),
    'UVUoOQL9SeI': ('Queen',                     'Bohemian Rhapsody'),
    'HLWntfUjKls': ('The Beatles',               'Penny Lane'),
    'PMQLWfvL3rY': ('Creedence Clearwater Revival', 'Have You Ever Seen the Rain'),
    'crHMq5HZkxk': ('John Mayer',                'Gravity'),
    'spreYrQA26s': ('The Foundations',           'Build Me Up Buttercup'),
    'A6s_-brGJck': ('Bruno Mars ft. Travie McCoy', 'Billionaire'),
    'yITT5_0RbK8': ('Zach Bryan',               'Long Island'),
    'OqwTNevdPGo': ('Pearl Jam',                 'Last Kiss'),
    'v_NeKzsclQ0': ('Red Hot Chili Peppers',     'Dark Necessities'),
}

# ── Cleaning helpers ─────────────────────────────────────────────────────────

# Ordered list of patterns to strip from the right of the title.
# Applied repeatedly until stable.
_STRIP_RE = re.compile(
    r'''(?ix)
    \s*
    (?:
        \|.*$                                          # | and everything after
        | \[(?:easy\s+)?piano\s+tutorial[s]?[^\]]*\]  # [Easy Piano Tutorial ...]
        | \((?:slow\s+)?(?:easy\s+)?piano\s+tutorial[s]?\)  # (Easy Piano Tutorial)
        | \(piano\s+tutorial\)
        | \(slow\s+easy\s+piano\s+tutorial\)
        | \(synthesia[^)]*\)
        | [-–]\s*(?:slow\s*[&]?\s*)?(?:very\s+)?easy\s+piano\s*(?:chords?\s+)?tutorial[s]?(?:\s+by\s+\S+(?:\s+\S+)*)?
        | [-–]\s*(?:slow\s+)?easy\s+piano\s+tutorial[s]?
        | [-–]\s*piano\s+tutorial[s]?(?:\s*\+\s*sheets?)?
        | [-–]\s*easy\s+piano\s+with\s+chords
        | \s+easy\s+piano\s+tutorial[s]?$
        | \s+easy\s+piano$
        | \s+easy\s+mode$
        | \s+piano\s+tutorial[s]?(?:\s*\+\s*sheets?)?$
        | \s+with\s+chords$
        | \s*\+\s*sheets?$
        | \|\|$                                        # trailing ||
        | \[?\s*hd\s*\]?                               # [ HD ]
        | \s+easy\s+piano\s+chords?\s+tutorial\s+by\s+piano\s+fun\s+play$
        | \s+easy\s+piano\s+tutorial\s*\+\s*sheet\s+music\s+by\s+\w+$
        | \s+slow\s+easy\s+piano\s+tutorial$
        | \s+easy\s+piano[!]?$
        | \s*\|\s*medium$
    )
    ''',
    re.IGNORECASE | re.VERBOSE,
)

def clean_title(raw):
    # Strip after first | quickly
    t = raw.split('|')[0].strip()  # wait, we already have the raw title field
    # Actually raw here is already just the title portion - but let's also strip pipe content
    t = re.sub(r'\s*\|.*$', '', raw).strip()

    # Normalize weird spacing in parens like "( TIME OF YOUR LIFE )"
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)

    # Apply strip pattern until stable
    prev = None
    while prev != t:
        prev = t
        t = _STRIP_RE.sub('', t).strip()

    # Strip trailing dash
    t = t.rstrip(' -–').strip()
    # Collapse multiple spaces
    t = re.sub(r'\s{2,}', ' ', t)
    return t


def smart_case(s):
    """Title-case only if the string is ALL CAPS; leave mixed case alone."""
    if s == s.upper() and len(s) > 1:
        # title() capitalizes after apostrophes weirdly ("Won'T") — fix it
        result = s.title()
        result = re.sub(r"'([A-Z])", lambda m: "'" + m.group(1).lower(), result)
        return result
    return s


def parse_entry(video_id, raw_title, duration_str):
    """Return (artist, title, duration_sec) or raise ValueError."""
    dur = int(float(duration_str)) if duration_str and duration_str != 'NA' else None

    # Manual override takes priority
    if video_id in OVERRIDES:
        artist, title = OVERRIDES[video_id]
        return artist, title, dur

    cleaned = clean_title(raw_title)

    # "Song ~ Artist" pattern
    if ' ~ ' in cleaned:
        left, right = cleaned.split(' ~ ', 1)
        right = re.sub(r'\s*\(.*?\)$', '', right).strip()  # drop trailing (...)
        return smart_case(right), smart_case(left), dur

    # "Title (Artist)" — artist in parens with no preceding dash
    m = re.fullmatch(r'(.+?)\s+\(([^)]+)\)', cleaned)
    if m and ' - ' not in m.group(1):
        return smart_case(m.group(2).strip()), smart_case(m.group(1).strip()), dur

    # "Artist - Song" — split on first dash
    if ' - ' in cleaned:
        artist_raw, song_raw = cleaned.split(' - ', 1)
        # Drop "(Tears For Fears)"-style credits from artist field of song side
        song_clean = re.sub(r'\s*\([^)]*\)$', '', song_raw).strip()
        return smart_case(artist_raw.strip()), smart_case(song_clean), dur

    # No separator — flag it
    return None, smart_case(cleaned), dur


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    db = SessionLocal()
    added = 0
    skipped = 0
    flagged = []

    for raw_line in RAW.strip().splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        parts = raw_line.split('|')
        if len(parts) < 4:
            flagged.append((raw_line, 'could not split on |'))
            continue

        video_id   = parts[0].strip()
        raw_title  = parts[1].strip()
        duration_s = parts[3].strip()

        try:
            artist, title, duration_sec = parse_entry(video_id, raw_title, duration_s)
        except Exception as e:
            flagged.append((raw_title, str(e)))
            continue

        if artist is None:
            flagged.append((f'{raw_title} [id={video_id}]', 'no artist/separator found'))

        # Skip if already in DB by video_id
        existing = db.query(Song).filter(Song.youtube_video_id == video_id).first()
        if existing:
            skipped += 1
            continue

        db.add(Song(
            title=title or raw_title,
            artist=artist or 'Unknown',
            difficulty=Difficulty.beginner,
            duration_sec=duration_sec or 0,
            source_type=SourceType.youtube,
            youtube_video_id=video_id,
            hand_mode=HandMode.both,
            genre='Pop',
        ))
        added += 1

    db.commit()
    db.close()

    print(f"\n✓ Added {added} songs  |  {skipped} already existed\n")

    if flagged:
        print(f"⚠  {len(flagged)} entries need manual review:")
        for item, reason in flagged:
            print(f"   • {item!r}  → {reason}")
    else:
        print("✓ All entries parsed cleanly.")


if __name__ == '__main__':
    main()
