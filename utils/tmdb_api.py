import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List


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
            Dict[str, any]: a dictionary containing:
                - 'cast': List of cast member dictionaires.
                - 'crew': List of crew member dictionaires.

        Raises:
            requests.HTTPError: If the HTTP request to TMDB fails.
        """
        url = f"{self.base_url}/movie/{movie_id}/credits"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def get_movie_embed_data(self, title: str, year=None, include_adult: bool = True):
        pass


api = TMDbAPI()
movie_creds = api.get_movie_credits(940721)
print(movie_creds)
