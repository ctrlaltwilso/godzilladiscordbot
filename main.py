import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
assert GUILD_ID is not None, "GUILD_ID not set in .env!"
assert TOKEN is not None, "DISCORD_TOKEN not set!"


class GojiraBot(commands.Bot):
    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                cog_path = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(cog_path)
                    print(f"Loaded cog: {cog_path}")
                except Exception as e:
                    print(f"Failed to load cog {cog_path}: {e}")


intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True
bot = GojiraBot(command_prefix="!", intents=intents)


# TODO: Implement logger for calls
def log_action(action: str, user: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {user}: {action}")


# Sync API 2.0 slash commands
@bot.event
async def on_ready():
    # Log guilds
    print(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        print("Bot is in guild:", guild.id, guild.name)


bot.run(TOKEN)
