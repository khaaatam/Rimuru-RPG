import discord
from discord import app_commands
from discord.ext import commands

class Quest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLERS ---
    @app_commands.command(name="quests", description="Menampilkan daftar quest yang tersedia.")
    async def quests_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = self.bot.logic_handler._quests_list_logic()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quest", description="Mengambil atau melihat info quest.")
    @app_commands.describe(action="Pilih 'ambil' atau 'info'", quest_id="ID quest yang ingin diambil (opsional)")
    async def quest_slash(self, interaction: discord.Interaction, action: str, quest_id: str = None):
        # ephemeral=True membuat respons hanya terlihat oleh Anda
        await interaction.response.defer(ephemeral=True)
        
        hasil = ""
        action = action.lower()

        if action == 'ambil':
            if not quest_id:
                await interaction.followup.send("Anda harus memasukkan ID quest untuk diambil.")
                return
            hasil = self.bot.logic_handler._quest_ambil_logic(interaction.user.id, quest_id)
        elif action == 'info':
            hasil = self.bot.logic_handler._quest_info_logic(interaction.user.id)
        else:
            hasil = "Aksi tidak valid. Gunakan 'ambil' atau 'info'."
        
        # --- BAGIAN YANG DIPERBAIKI ---
        # Cek apakah 'hasil' adalah sebuah Embed atau teks biasa
        if isinstance(hasil, discord.Embed):
            # Jika Embed, kirim menggunakan parameter 'embed'
            await interaction.followup.send(embed=hasil)
        else:
            # Jika hanya teks, kirim seperti biasa
            await interaction.followup.send(hasil)

    # --- PREFIX COMMAND HANDLERS ---
    @commands.command(name="quests", aliases=['qlist'])
    async def quests_prefix(self, ctx: commands.Context):
        embed = self.bot.logic_handler._quests_list_logic()
        await ctx.send(embed=embed)

    @commands.command(name="quest", aliases=['q'])
    async def quest_prefix(self, ctx: commands.Context, action: str = None, *, quest_id: str = None):
        if not action:
            await ctx.send("Gunakan format: `rquest <ambil/info> [id_quest]`")
            return
        
        # Inisialisasi 'hasil'
        hasil = ""
        action = action.lower()

        if action == 'ambil':
            if not quest_id:
                await ctx.send("Anda harus memasukkan ID quest untuk diambil.")
                return
            hasil = self.bot.logic_handler._quest_ambil_logic(ctx.author.id, quest_id)
        elif action == 'info':
            hasil = self.bot.logic_handler._quest_info_logic(ctx.author.id)
        else:
            hasil = "Aksi tidak valid. Gunakan 'ambil' atau 'info'."
        
        # --- BAGIAN YANG DIPERBAIKI ---
        # Cek apakah 'hasil' adalah sebuah Embed atau teks biasa
        if isinstance(hasil, discord.Embed):
            # Jika Embed, kirim teks mention di 'content' dan embed di 'embed'
            await ctx.send(f"{ctx.author.mention}", embed=hasil)
        else:
            # Jika hanya teks, kirim seperti biasa
            await ctx.send(f"{ctx.author.mention}, {hasil}")

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        Quest(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )