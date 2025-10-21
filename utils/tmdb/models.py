from dataclasses import dataclass, field
from typing import List


@dataclass
class CrewMember:
    name: str = ""
    job: str = ""
    department: str = ""


@dataclass
class CastMember:
    name: str = ""
    character: str = ""
    order: int = 999


@dataclass
class ProductionCompany:
    name: str = ""
    logo_path: str = ""


@dataclass
class ParsedCredits:
    directors: List[CrewMember]
    writers: List[CrewMember]
    actors: List[CastMember]


@dataclass
class MovieDetails:
    title: str = ""
    release_date: str = ""
    summary: str = ""
    runtime: int = 0
    budget: int = 0
    tmdb_rating: float = 0
    revenue: int = 0
    genres: List[str] = field(default_factory=list)
    poster_path: str = ""
    production_companies: List[ProductionCompany] = field(default_factory=list)
    original_language: str = ""
    origin_countrys: List[str] = field(default_factory=list)
