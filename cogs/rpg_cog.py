import discord
from discord import app_commands
from discord.ext import commands

# Impor fungsi logika dari file utama Anda nanti
# (Untuk sekarang, kita asumsikan file utama akan menyediakannya)

class RPG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMANDS ---
    @app_commands.command(name="jelajah", description="Pergi menjelajah untuk mencari Gold dan XP.")
    async def jelajah_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Kita panggil fungsi logika dari bot utama
        hasil = self.bot.logic_handler._jelajah_logic(interaction.user.id)
        if hasil:
            await interaction.followup.send(f"{interaction.user.mention}, {hasil.lower()}")
        else:
            await interaction.followup.send("Anda belum membuat karakter! Gunakan `/mulai`.", ephemeral=True)

    @app_commands.command(name="hunting", description="Berburu monster di zona tertentu.")
    @app_commands.describe(zona="ID zona tempat Anda ingin berburu (contoh: hutan)")
    async def hunting_slash(self, interaction: discord.Interaction, zona: str):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._hunting_logic(interaction.user.id, zona)
        if hasil:
            await interaction.followup.send(f"{interaction.user.mention}\n{hasil}")
        else:
            await interaction.followup.send("Anda belum membuat karakter!", ephemeral=True)

    @app_commands.command(name="zona", description="Melihat daftar zona berburu.")
    async def zona_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = self.bot.logic_handler._zona_list_logic()
        await interaction.followup.send(embed=embed)

    # --- PREFIX COMMANDS ---
    @commands.command(name="jelajah", aliases=["adv"])
    async def jelajah_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._jelajah_logic(ctx.author.id)
        if hasil:
            await ctx.send(f"{ctx.author.mention}, {hasil.lower()}")
        else:
            await ctx.send("Anda belum membuat karakter! Gunakan `rmulai`.")

    @commands.command(name="hunting", aliases=["hunt", "h"])
    async def hunting_prefix(self, ctx: commands.Context, zona: str = None):
        hasil = self.bot.logic_handler._hunting_logic(ctx.author.id, zona)
        if hasil:
            await ctx.send(f"{ctx.author.mention}\n{hasil}")
        else:
            await ctx.send("Anda belum membuat karakter!")
            
    @commands.command(name="zona")
    async def zona_prefix(self, ctx: commands.Context):
        embed = self.bot.logic_handler._zona_list_logic()
        await ctx.send(embed=embed)

# Fungsi ini wajib ada di setiap file cog untuk memuatnya
async def setup(bot: commands.Bot):
    # Kita akan membuat logic_handler di file utama
    await bot.add_cog(RPG(bot), guild=discord.Object(id=int(bot.GUILD_ID)) if bot.GUILD_ID else None)