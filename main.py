import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from dotenv import load_dotenv
from movie_manager.movie_manager import update_movie, mark_not_owned, list_movies
from datetime import datetime
import os


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
assert GUILD_ID is not None, "GUILD_ID not set in .env!"
assert TOKEN is not None, "DISCORD_TOKEN not set!"

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


def log_action(action: str, user: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {user}: {action}")


class MovieUpdater(View):
    def __init__(self, title: str, year: int):
        super().__init__(timeout=None)
        self.title = title
        self.year = year

    @discord.ui.button(label="Owned", style=discord.ButtonStyle.success)  # type: ignore
    async def mark_owned(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        result = update_movie(title=self.title, year=self.year)
        await interaction.response.send_message(result)

    @discord.ui.button(label="Not Owned", style=discord.ButtonStyle.danger)  # type: ignore
    async def marked_not_owned(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        result = mark_not_owned(title=self.title, year=self.year)
        await interaction.response.send_message(result)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = "Action Canceled."
        await interaction.response.send_message(result)


class MovieView(View):
    message: discord.Message | None

    def __init__(self, movies, per_page=20):
        super().__init__(timeout=300)
        self.movies = movies
        self.per_page = per_page
        self.page = 0

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
            if self.message:
                await self.message.edit(view=self)

    def make_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        current_movies = self.movies[start:end]

        embed = discord.Embed(
            title=f"Godzilla Movies (Page {self.page + 1}/{(len(self.movies) - 1) // self.per_page + 1})",
            color=discord.Color.blurple(),
        )

        for movie in current_movies:
            own = "✅" if movie["own"] == "Yes" else "❌"
            embed.add_field(
                name=f"{own} {movie['title']} ({movie['year']})",
                value="",
                inline=False,
            )
        return embed

    @discord.ui.button(label="⬅️ Prev.", style=discord.ButtonStyle.secondary)
    async def prev_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="➡️ next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if (self.page + 1) * self.per_page < len(self.movies):
            self.page += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)


@bot.tree.command(name="movie", description="Change ownership of a movie")
@app_commands.describe(
    year="The year the movie was released", title="The title of the movie"
)
async def movie(interaction: discord.Interaction, year: int, title: str):
    embed = discord.Embed(
        title=f"{title} ({year})",
        description="Use buttons to mark Owned or Not Owned.",
        color=discord.Color.green(),
    )

    await interaction.response.send_message(embed=embed, view=MovieUpdater(title, year))


# Sync API 2.0 slash commands
@bot.event
async def on_ready():
    guild = discord.Object(id=int(GUILD_ID))  # type: ignore
    print(f"Logged in as {bot.user}")
    try:
        bot.tree.clear_commands(guild=guild)
        print("Cleared Guild Commands.")
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# Legacy
# TODO: Can Remove ?
@bot.command()
async def own(ctx, year: int, *, title: str):
    """Mark movie as owned."""
    result = update_movie(title=title, year=year)
    log_action(f"Marked '{title}' ({year}) as owned.", ctx.author.name)
    await ctx.send(result)


# Legacy
# TODO: Can remove ?
@bot.command()
async def notown(ctx, year: int, *, title: str):
    """Marks movies as not owned."""
    result = mark_not_owned(title=title, year=year)
    await ctx.send(result)


# TODO: Change to paginated response and remove ascii table
# TODO: Will need class to handle view
# TODO: Change to Slash Command
# TODO: Check results, list movies no longer does it
@bot.command()
async def movies(ctx, *keywords):
    keyword = " ".join(keywords)
    movies = list_movies(keyword=keyword)
    if not movies:
        await ctx.send("ℹ️ No movies found.")

    view = MovieView(movies)
    await ctx.send(embed=view.make_embed(), view=view)


# Embed Additions
# TODO: Change to slash Command
@bot.command()
async def vegetables(ctx):
    e_message = discord.Embed(
        title="Gojira Butler ",
        type="rich",
        description="Godzilla eats his vegetables.",
        color=discord.Color.green(),
    )
    image_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWYwd2w1Y3RkdnA1bjN0ZTJ4cXFieWFiZHN0M3ptbmd5aXR5bW1yeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2A0jXvUa3KOufBYT53/giphy.gif"
    e_message.set_image(url=image_url)

    await ctx.send(embed=e_message)


bot.run(TOKEN)
