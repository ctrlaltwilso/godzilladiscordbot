import discord
from discord.ext import commands
import os

GUILD_ID = os.getenv("GUILD_ID")


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
        except commands.ExtensionNotLoaded:
            pass

        await self.bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(f"Reloaded {cog_name} successfully.")

    @commands.command()
    @commands.is_owner()
    async def clear_commands(self, ctx):
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()

        guild_obj = discord.Object(id=int(GUILD_ID))  # type: ignore
        self.bot.tree.clear_commands(guild=guild_obj)
        await self.bot.tree.sync(guild=guild_obj)

        await ctx.send("All commands cleared from Discord")


async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))
