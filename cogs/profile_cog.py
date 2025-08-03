import discord
from discord import app_commands
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLERS ---
    @app_commands.command(name="mulai", description="Membuat karakter dan memulai petualangan!")
    async def mulai_slash(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Memanggil fungsi logika dari LogicHandler di main.py
        hasil = self.bot.logic_handler._mulai_logic(interaction.user.id)
        
        if "Selamat datang" in hasil:
            await interaction.followup.send(f"{hasil} {interaction.user.mention}!")
        else:
            await interaction.followup.send(hasil)

    @app_commands.command(name="profil", description="Melihat statistik karakter Anda.")
    async def profil_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = self.bot.logic_handler._profil_logic(interaction.user.id, interaction.user.name, interaction.user.avatar.url)
        if embed is not None:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Anda belum membuat karakter! Gunakan `/mulai`.", ephemeral=True)

    # --- PREFIX COMMAND HANDLERS ---
    @commands.command(name="mulai", aliases=["start"])
    async def mulai_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._mulai_logic(ctx.author.id)
        if "Selamat datang" in hasil:
            await ctx.send(f"{hasil} {ctx.author.mention}!")
        else:
            await ctx.send(hasil)

    @commands.command(name="profil", aliases=["profile", "stats", "p"])
    async def profil_prefix(self, ctx: commands.Context):
        embed = self.bot.logic_handler._profil_logic(ctx.author.id, ctx.author.name, ctx.author.avatar.url)
        if embed is not None:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Anda belum membuat karakter! Gunakan `rmulai`.")

# Fungsi setup untuk memuat Cog
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        Profile(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )