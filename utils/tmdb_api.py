import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List, TypedDict


class CrewMember(TypedDict, total=False):
    name: str
    job: str
    department: str


class CastMember(TypedDict, total=False):
    name: str
    character: str
    order: int


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
        # normalize cast member data
        return {
            "name": raw.get("name", ""),
            "character": raw.get("character", ""),
            "order": raw.get("order", 999),
        }

    def _to_crew_member(self, raw: Dict[str, Any]) -> CrewMember:
        # normalize crew data
        return {
            "name": raw.get("name", ""),
            "department": raw.get("department", ""),
            "job": raw.get("job", ""),
        }

    def _filter_crew_by_job(
        self,
        clean_crew: List[CrewMember],
        department_substring: str,
        job_substring: Optional[str] = None,
    ) -> List[CrewMember]:
        results: List[CrewMember] = [
            member
            for member in clean_crew
            if department_substring in member.get("department", "").lower()
            and (
                job_substring is None or job_substring in member.get("job", "").lower()
            )
        ]

        return results

    def parse_movie_credits(
        self, credits: Dict[str, Any], top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Returns parsed credits data from TMDB

        Parameters:
            credits (Dict[str, Any]): Response from TMDB /movie/{movie_id}/credits endpoint.
            top_n (int): the number of top actors to return based on order (default=5)

        Returns:
            Dict[str, List[Dict[str, Any]]]: a dictionary containing:
                - 'directors': List of crew members with job='Director'
                - 'writers': List of crew members with job='Writer'
                - 'actors': List of top N case members, sorted by 'order'
        """
        raw_cast: List[Dict[str, Any]] = credits.get("cast") or []
        raw_crew: List[Dict[str, Any]] = credits.get("crew") or []

        clean_cast: List[CastMember] = [
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
        actors = sorted(clean_cast, key=lambda x: x.get("order", 999))[:top_n]

        return {
            "directors": directors,
            "writers": writers,
            "actors": actors,
        }

    def get_movie_embed_data(self, title: str, year=None, include_adult: bool = True):
        # search = self.search_movie(title, year)
        # self.get_movie_details(search)
        # self.get_movie_img()
        pass


api = TMDbAPI()
movie_creds = api.get_movie_credits(940721)
pmc = api.parse_movie_credits(movie_creds)
print(pmc)
