import discord
from discord.ext import commands
from discord import app_commands
from movie_manager.movie_manager import list_movies
from utils.tmdb.tmdb_api import TMDbAPI
from views.movie_views import MovieUpdater, MovieView
import os
from typing import Optional

GUILD_ID = os.getenv("GUILD_ID")
api = TMDbAPI()


class Movies(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    movie_group = app_commands.Group(name="movie", description="Movie related commands")

    @movie_group.command(name="own", description="Change ownership of a movie")
    @app_commands.describe(
        year="The year the movie was released", title="The title of the movie"
    )
    async def own_movie(self, interaction: discord.Interaction, year: int, title: str):
        embed = discord.Embed(
            title=f"{title} ({year})",
            description="Use buttons to mark Owned or Not Owned.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(
            embed=embed, view=MovieUpdater(title, year)
        )

    @movie_group.command(
        name="list", description="List Godzilla Films, can search by keyword"
    )
    async def return_movies(self, interaction: discord.Interaction, keyword: str = ""):
        # keyword = " ".join(keyword)
        movies = list_movies(keyword=keyword)
        if not movies:
            await interaction.response.send_message("ℹ️ No movies found.")
            return
        view = MovieView(movies)
        await interaction.response.send_message(embed=view.make_embed(), view=view)

    # ---- TMDb Movie Lookup ---- #
    @movie_group.command(name="info", description="Get movie details from TMDB")
    @app_commands.describe(
        title="Title of the movie", year="Year the movie was released"
    )
    async def movie_command(self, interaction, title: str, year: Optional[int] = None):
        lookup = api.get_movie_embed_data(title, year)

        if not lookup.success:
            await interaction.response.send_message("Movie not found.")

        details = lookup.details
        credits = lookup.credits
        poster = lookup.poster
        print("Poster URL: ", poster)

        genres = (
            ", ".join(f"{genre}" for genre in details.genres) or "No genres available."
        )

        directors = (
            "\n".join(
                f"{director.job}: {director.name}" for director in credits.directors
            )
            or "No director information available."
        )

        writers = (
            "\n".join(f"{writer.job}: {writer.name}" for writer in credits.writers)
            or "No writer information available."
        )

        main_cast = (
            "\n".join(f"{actor.name} as {actor.character}" for actor in credits.actors)
            or "No cast information available."
        )

        embed = discord.Embed(title=details.title, description=details.summary)
        embed.set_image(url=poster)
        embed.add_field(name="Genres:", value=genres)
        embed.add_field(name="Director(s):", value=directors)
        embed.add_field(name="Writer(s):", value=writers)
        embed.add_field(name="Main Cast:", value=main_cast, inline=False)

        await interaction.response.send_message(embed=embed)

    # Load Commands
    async def cog_load(self) -> None:
        guild = discord.Object(id=int(GUILD_ID))  # type: ignore
        if not self.bot.tree.get_command("movie", guild=guild):
            self.bot.tree.add_command(self.movie_group, guild=guild)
        # if not self.bot.tree.get_command("movie"):
        #     self.bot.tree.add_command(self.movie_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(Movies(bot))
