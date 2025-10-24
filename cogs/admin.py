import discord
from discord.ext import commands
from discord import app_commands
import os

GUILD_ID = os.getenv("GUILD_ID")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.GUILD_ID = GUILD_ID

    admin_group = app_commands.Group(name="admin", description="Admin only commands")

    # For slash commands
    def is_owner(self):
        async def predicate(interaction: discord.Interaction, *args, **kwargs) -> bool:
            if isinstance(interaction.client, commands.Bot):
                return await interaction.client.is_owner(interaction.user)
            return False

        return app_commands.check(predicate)

    @admin_group.command(
        name="sync", description="Sync slash commands(owner only, don't use)"
    )
    @is_owner.__get__(object)()
    async def sync_commands(self, interaction: discord.Interaction):
        guild = discord.Object(id=int(self.GUILD_ID))  # type: ignore
        self.bot.tree.copy_global_to(guild=guild)
        synced = await self.bot.tree.sync(guild=guild)
        await interaction.response.send_message(
            f"Synced {len(synced)} commands.", ephemeral=True
        )
        guild_cmds = await self.bot.tree.fetch_commands(guild=guild)
        global_cmds = await self.bot.tree.fetch_commands()

        print(f"Guild Commands: {guild_cmds}\nGlobal commands: {global_cmds}")

    # For non slash commands
    @staticmethod
    def isowner_ctx():
        async def predicate(ctx: commands.Context):
            print("Author:", ctx.author)
            return await ctx.bot.is_owner(ctx.author)

        return commands.check(predicate)

    @commands.command()
    @isowner_ctx()
    async def sinkit(self, ctx):
        guild = discord.Object(id=int(self.GUILD_ID))  # type: ignore

        print("DEBUG: Commands in bot.tree before sync ===")
        for cmd in self.bot.tree.walk_commands():
            print(f"{cmd.name} {type(cmd)}")

        self.bot.tree.copy_global_to(guild=guild)
        synced = await self.bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands.")
        for cmd in synced:
            print(f"- {cmd.name}")

        global_synced = await self.bot.tree.sync()
        print(f"Global synced: {len(global_synced)}")

        await ctx.send(f"Synced {len(synced)} commands.")

    @commands.command()
    @isowner_ctx()
    async def clearc(self, ctx):
        guild = discord.Object(id=int(GUILD_ID))  # type: ignore
        self.bot.tree.clear_commands(guild=guild)
        self.bot.tree.clear_commands(guild=None)

        await self.bot.tree.sync(guild=guild)
        await self.bot.tree.sync(guild=None)

        guild_cmds = await self.bot.tree.fetch_commands(guild=guild)
        global_cmds = await self.bot.tree.fetch_commands()

        print(f"Guild Commands: {guild_cmds}\nGlobal commands: {global_cmds}")
        await ctx.send("Cleared commands")

    async def cog_load(self) -> None:
        guild = discord.Object(id=int(GUILD_ID))  # type: ignore
        if not self.bot.tree.get_command("admin", guild=guild):
            self.bot.tree.add_command(self.admin_group, guild=guild)
        # if not self.bot.tree.get_command("admin"):
        #     self.bot.tree.add_command(self.admin_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
