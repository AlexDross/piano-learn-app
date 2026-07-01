from sqlalchemy import Column, Integer, String, Text, Enum, Boolean
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class Difficulty(str, enum.Enum):
    beginner = "beginner"
    easy = "easy"
    intermediate = "intermediate"
    hard = "hard"


class SourceType(str, enum.Enum):
    midi = "midi"
    youtube = "youtube"


class HandMode(str, enum.Enum):
    right_only = "right_only"
    left_only = "left_only"
    both = "both"


def _enum(py_enum):
    return Enum(py_enum, native_enum=False)


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    difficulty = Column(_enum(Difficulty), nullable=False)
    duration_sec = Column(Integer, nullable=False)
    source_type = Column(_enum(SourceType), nullable=False)
    midi_file_path = Column(String, nullable=True)
    youtube_video_id = Column(String, nullable=True)
    hand_mode = Column(_enum(HandMode), nullable=False, default=HandMode.both)
    genre = Column(String, nullable=False)
    note_data_json = Column(Text, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False)
