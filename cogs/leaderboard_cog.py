import discord
from discord import app_commands
from discord.ext import commands

class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLER ---
    @app_commands.command(name="leaderboard", description="Menampilkan papan peringkat pemain teratas.")
    async def leaderboard_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Memanggil fungsi logika dari LogicHandler
        # Kita perlu memberikan 'self.bot' agar bisa mengambil nama pengguna
        hasil = await self.bot.logic_handler._leaderboard_logic(self.bot)
        
        if isinstance(hasil, discord.Embed):
            await interaction.followup.send(embed=hasil)
        else:
            await interaction.followup.send(hasil)

    # --- PREFIX COMMAND HANDLER ---
    @commands.command(name="leaderboard", aliases=['lb', 'top'])
    async def leaderboard_prefix(self, ctx: commands.Context):
        # Memanggil fungsi logika yang sama
        hasil = await self.bot.logic_handler._leaderboard_logic(self.bot)

        if isinstance(hasil, discord.Embed):
            await ctx.send(embed=hasil)
        else:
            await ctx.send(hasil)

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        Leaderboard(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )