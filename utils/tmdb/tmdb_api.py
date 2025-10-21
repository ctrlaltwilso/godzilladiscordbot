import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from models import (
    CrewMember,
    CastMember,
    MovieDetails,
    ProductionCompany,
    ParsedCredits,
)
from pprint import pprint


class TMDbAPI:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("TMDB_ACCESS")
        assert self.token, "TMDB_ACCESS is not set!"
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.base_url = "https://api.themoviedb.org/3"
        self.base_img = "https://image.tmdb.org/t/p/w500"

    def search_movie(
        self, title: str, year: Optional[int] = None, include_adult: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search TMDB for a movie by title and optional release year.

        Parameters:
            title (str): The title of the movie.
            year (Optional[int]): The year of the movie (optional).
            include_adult (bool, default=True): include adult (R/NC-17) content.

        Returns:
            List[Dict[str, Any]]: A list of dictionary representing matching movies:
                - The dictionary contains details like 'id', 'title', 'release_date', etc.
        """
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "include_adult": include_adult,
        }

        if year:
            params["primary_release_year"] = year

        r = requests.get(url, params=params, headers=self.headers)
        return r.json().get("results", [])

    def get_movie_by_title(
        self, title: str, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single movie from TMDB that matches the exact title (case-insensitive).

        This function wraps `search_movie` and returns the first movies whose title matches
        exactly the provided `title`. You can optionally provide a release year to narrow
        the search. Returns None if no exact match is found.

        Parameters:
            title (str): The exact title of the move to search.
            year (Optional[int]): Optional release year.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the movie details if found,
            or None if no exact match exists.
        """
        results = self.search_movie(title, year)
        for movie in results:
            if movie.get("title", "").lower() == title.lower():
                return movie
        return None

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        Returns TMDB movie information through ID.

        Parameters:
            movie_id (int): TMDB movie ID.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'genres': movie genres associated with the film.
                - 'origin_country': movie's origin.
                - 'overview': short description of the movie.
                - 'budget': movies budget.
                - 'revenue': amount movie made.
                - 'runtime': movie length in minutes.
                - 'title': the movie title.
                - 'vote_average': TMDB rating.

        Raises:
            requests.HTTPError: If the HTTP request to TMDB fails.
        """
        url = f"{self.base_url}/movie/{movie_id}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def parse_movie_details(self, raw: Dict[str, Any]) -> MovieDetails:
        """
        Nomarlizes raw TMDB movie details into a MovieDetails dataclass.

        Parameters:
            raw (Dict[str, Any]): Raw JSON from TMDB movie/{movie_id} endpoint.

        Returns:
            MovieDetails: Dataclass containing nomralized movie details, including:
                - title (str)
                - release_date (str)
                - summary (str)
                - runtime (int)
                - budget (int)
                - revenue (int)
                - tmdb_rating (float)
                - genres (List[str])
                - production_companies (List[ProductionCompany])
                - original_language (str)
                - origin_country (List[str])
        """
        return MovieDetails(
            title=raw.get("title", ""),
            release_date=raw.get("release_date", ""),
            summary=raw.get("overview", ""),
            runtime=raw.get("runtime") or 0,
            budget=raw.get("budget") or 0,
            revenue=raw.get("revenue") or 0,
            tmdb_rating=raw.get("rating") or 0,
            genres=[g.get("name") for g in raw.get("genres", []) if "name" in g],
            poster_path=raw.get("poster_path", ""),
            production_companies=[
                ProductionCompany(
                    name=p.get("name", ""), logo_path=p.get("logo_path", "")
                )
                for p in raw.get("production_companies", [])
                if isinstance(p, dict)
            ],
            original_language=raw.get("original_language", ""),
            origin_countrys=raw.get("origin_country", []),
        )

    def get_movie_img(self, img_address: str) -> str | None:
        # Return full URL for a movie image
        if img_address:
            return f"{self.base_url}{img_address}"
        return None

    def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """
        Fetch the credits (cast and crew) for a movie from TMDB.

        Parameters:
            movie_id (int): The TMDB ID of the movie.

        Returns:
            Dict[str, Any]: a dictionary containing:
                - 'cast': List of cast member dictionaires.
                - 'crew': List of crew member dictionaires.

        Raises:
            requests.HTTPError: If the HTTP request to TMDB fails.
        """
        url = f"{self.base_url}/movie/{movie_id}/credits"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def _to_cast_member(self, raw: Dict[str, Any]) -> CastMember:
        """
        Convert a raw TMDB dict into a CastMember dataclass

        Parameters:
            raw(Dict[str, Any]): Raw cast data from TMDB API.

        Returns:
            CastMember: Dataclass containing 'name', 'chatacter', and 'order'
        """
        return CastMember(
            name=raw.get("name", ""),
            character=raw.get("character", ""),
            order=raw.get("order", 999),
        )

    def _to_crew_member(self, raw: Dict[str, Any]) -> CrewMember:
        """
        Converts a raw TMDB crew member dictionary into a CrewMember Dataclass

        Parameters:
            raw (Dict[str, Any]): Raw crew member data from TMDB API.

        Returns:
            CrewMember: Dataclass containing:
                - name (str)
                - department (str)
                - job (str)
        """
        return CrewMember(
            name=raw.get("name", ""),
            department=raw.get("department", ""),
            job=raw.get("job", ""),
        )

    def _filter_crew_by_job(
        self,
        clean_crew: List[CrewMember],
        department_substring: str,
        job_substring: Optional[str] = None,
    ) -> List[CrewMember]:
        """
        Filters a list of CrewMember dataclasses by department and optionally by job.

        Parameters:
            clean_crew (List[CrewMember]): List of normalized crew members.
            department_substring (str): Substring to match in the department field.
            job_substring (Optional[str]): Substring to match in the job field. If None, ignores job.

        Returns:
            List[CrewMember]: Crew member matching the specified filters.
        """
        results: List[CrewMember] = [
            member
            for member in clean_crew
            if department_substring in member.department.lower()
            and (job_substring is None or job_substring in member.job.lower())
        ]

        return results

    def parse_movie_credits(
        self, credits: Dict[str, Any], top_n: int = 5
    ) -> ParsedCredits:
        """
        Parses TMDB movie credits and returns structured dataclasses.

        Parameters:
            credits (Dict[str, Any]): Raw TMDB credits JSON from /movie/{movie_id}/credits
            top_n (int, optional): the number of top actors to return based on order (default=5)

        Returns:
            ParsedCredits: Dataclass containing:
                - directors (List[CrewMember]): list of director(s)
                - writers (List[CrewMember]): list of writer(s)
                - actors (List[CastMember]): Top N main actors
        """
        raw_cast: List[Dict[str, Any]] = credits.get("cast") or []
        raw_crew: List[Dict[str, Any]] = credits.get("crew") or []

        clean_cast = [
            self._to_cast_member(c)
            for c in raw_cast
            if isinstance(c, dict) and "name" in c
        ]

        clean_crew: List[CrewMember] = [
            self._to_crew_member(m)
            for m in raw_crew
            if isinstance(m, dict) and "name" in m
        ]

        # Get Director(s)
        directors = self._filter_crew_by_job(clean_crew, "directing", "director")

        # Get Writer
        writers = self._filter_crew_by_job(clean_crew, "writing")

        # Get Top x main actors
        actors = sorted(clean_cast, key=lambda x: x.order)[:top_n]

        return ParsedCredits(
            directors=directors,
            writers=writers,
            actors=actors,
        )

    def get_movie_embed_data(self, title: str, year=None, include_adult: bool = True):
        # search = self.search_movie(title, year)
        # self.get_movie_details(search)
        # self.get_movie_img()
        pass


api = TMDbAPI()
movie_details = api.get_movie_details(940721)
pmd = api.parse_movie_details(movie_details)
movie_creds = api.get_movie_credits(940721)
pmc = api.parse_movie_credits(movie_creds)
print("Movie Information:")
pprint(pmd)
print("\nCast & Crew:")
pprint(pmc)
