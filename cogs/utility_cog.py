import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# --- FUNGSI LOGIKA INTI UNTUK HELP ---
def _help_logic(bot, guild):
    # Dapatkan daftar prefix dari bot
    prefixes = bot.command_prefix
    prefix_text = " atau ".join([f"`{p.strip()}`" for p in prefixes])

    # Buat embed dasar
    embed = discord.Embed(
        title="Bantuan Bot Rimuru RPG",
        description=f"Berikut adalah daftar perintah yang tersedia. Prefix saat ini adalah {prefix_text}.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=bot.user.avatar.url)

    # Menambahkan kategori perintah
    embed.add_field(
        name="👤 Perintah Karakter",
        value="`/mulai` atau `r!mulai` - Membuat karakter baru.\n"
              "`/profil` atau `r!profil` - Melihat profil karakter.",
        inline=False
    )
    embed.add_field(
        name="⚔️ Perintah Aksi RPG",
        value="`/jelajah` atau `r!jelajah` - Mencari gold dan XP secara acak.\n"
              "`/hunting` atau `r!hunting` - Melawan monster untuk hadiah.",
        inline=False
    )
    embed.add_field(
        name="💰 Perintah Ekonomi",
        value="`/harian` atau `r!harian` - Klaim hadiah gold harian.\n"
              "`/toko` atau `r!toko` - Menampilkan item di toko.\n"
              "`/inventaris` atau `r!inventaris` - Menampilkan item di tas Anda.\n"
              "`/beli <item_id> [jumlah]` atau `r!beli <item_id> [jumlah]` - Membeli item.\n"
              "`/gunakan <item_id>` atau `r!gunakan <item_id>` - Menggunakan item konsumsi.\n"
              "`/equip <item_id>` atau `r!equip <item_id>` - Memakai perlengkapan.",
        inline=False
    )
    embed.set_footer(text=f"Bot developed by JikaeL | {datetime.now().strftime('%d-%m-%Y')}")
    return embed

# --- KELAS COG ---
class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLER ---
    @app_commands.command(name="help", description="Menampilkan daftar semua perintah bot.")
    async def help_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = _help_logic(self.bot, interaction.guild)
        await interaction.followup.send(embed=embed)

    # --- PREFIX COMMAND HANDLER ---
    @commands.command(name="help", aliases=['bantuan'])
    async def help_prefix(self, ctx: commands.Context): # <-- PERBAIKAN ADA DI SINI
        embed = _help_logic(self.bot, ctx.guild)
        await ctx.send(embed=embed)

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        Utility(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )