import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLER ---
    @app_commands.command(name="heal", description="Menggunakan Ramuan Kesehatan untuk memulihkan HP.")
    async def heal_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._heal_logic(interaction.user.id)
        await interaction.followup.send(f"{interaction.user.mention}, {hasil}")

    # --- PREFIX COMMAND HANDLER ---
    @commands.command(name="heal")
    async def heal_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._heal_logic(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}, {hasil}")

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        General(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )