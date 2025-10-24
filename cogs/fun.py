import discord
from discord.ext import commands
from discord import app_commands
import os


GUILD_ID = os.getenv("GUILD_ID")


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    godzilla_group = app_commands.Group(
        name="godzilla", description="godzilla commands"
    )

    @godzilla_group.command(
        name="vegetables", description="make godzilla eat his vegetables"
    )
    async def eat_vegetables(self, interaction: discord.Interaction):
        e_message = discord.Embed(
            title="Gojira Butler ",
            type="rich",
            description="Godzilla eats his vegetables.",
            color=discord.Color.green(),
        )
        image_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWYwd2w1Y3RkdnA1bjN0ZTJ4cXFieWFiZHN0M3ptbmd5aXR5bW1yeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2A0jXvUa3KOufBYT53/giphy.gif"
        e_message.set_image(url=image_url)

        await interaction.response.send_message(embed=e_message)

    async def cog_load(self) -> None:
        guild = discord.Object(id=int(GUILD_ID))  # type: ignore
        if not self.bot.tree.get_command("godzilla", guild=guild):
            self.bot.tree.add_command(self.godzilla_group, guild=guild)
        # if not self.bot.tree.get_command("godzilla"):
        #     self.bot.tree.add_command(self.godzilla_group)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
