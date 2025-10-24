import discord
from discord.ui import View
from movie_manager.movie_manager import update_movie, mark_not_owned


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
