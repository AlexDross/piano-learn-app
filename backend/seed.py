from database import SessionLocal
from models import Song


def seed():
    db = SessionLocal()
    count = db.query(Song).count()
    db.close()
    if count == 0:
        print("Songs table is empty — run seed_youtube_playlist.py to populate.")
    else:
        print(f"Database has {count} song(s), skipping seed.")


if __name__ == "__main__":
    seed()
