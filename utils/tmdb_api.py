import requests
import os
from dotenv import load_dotenv


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

    def search_movie(self, title: str, year=None, include_adult: bool = True):
        url = f"{self.base_url}/search/movie"
        params = {
            "query": title,
            "include_adult": include_adult,
        }

        if year:
            params["primary_release_year"] = year

        r = requests.get(url, params=params, headers=self.headers)
        return r.json().get("results", [])

    def get_movie_details(self, movie_id: int):
        url = f"{self.base_url}/movie/"
        params = {"movie_id": movie_id}
        r = requests.get(url, params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()
