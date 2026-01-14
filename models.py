from dataclasses import dataclass, field
from typing import List

@dataclass
class SongList:
    name: str = ""
    songs: List[str] = field(default_factory=list)
    songs_count: int = 0
    duplicate_count: int = 0
    platform: str = ""

@dataclass
class Result:
    code: int
    msg: str
    data: object
