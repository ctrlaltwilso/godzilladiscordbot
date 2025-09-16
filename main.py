import discord
from discord.ext import commands
from dotenv import load_dotenv
from movie_manager.movie_manager import update_movie, mark_not_owned, list_movies
from datetime import datetime
import os


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
assert TOKEN is not None, "DISCORD_TOKEN not set!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


def log_action(action: str, user: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {user}: {action}")


@bot.command()
async def own(ctx, year: int, *, title: str):
    """Mark movie as owned."""
    result = update_movie(title=title, year=year)
    log_action(f"Marked '{title}' ({year}) as owned.", ctx.author.name)
    await ctx.send(result)


@bot.command()
async def notown(ctx, year: int, *, title: str):
    """Marks movies as not owned."""
    result = mark_not_owned(title=title, year=year)
    await ctx.send(result)


@bot.command()
async def movies(ctx, *keywords):
    keyword = " ".join(keywords)
    result = list_movies(keyword=keyword)
    await ctx.send(result)


bot.run(token=TOKEN)
