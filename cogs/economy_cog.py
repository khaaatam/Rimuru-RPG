import discord
from discord import app_commands
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # --- SLASH COMMANDS ---
    @app_commands.command(name="toko", description="Melihat item yang tersedia di toko.")
    async def toko_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Memanggil fungsi logika dari main.py melalui self.bot
        hasil = self.bot.logic_handler._toko_logic()
        if isinstance(hasil, discord.Embed):
            await interaction.followup.send(embed=hasil)
        else:
            await interaction.followup.send(hasil)

    @app_commands.command(name="inventaris", description="Melihat item yang Anda miliki.")
    async def inventaris_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._inventaris_logic(interaction.user.id, interaction.user.name, interaction.user.avatar.url)
        if isinstance(hasil, discord.Embed):
            await interaction.followup.send(embed=hasil)
        else:
            await interaction.followup.send(hasil)
            
    @app_commands.command(name="beli", description="Membeli item dari toko.")
    @app_commands.describe(item_id="ID item yang ingin dibeli", jumlah="Jumlah yang ingin dibeli (default 1)")
    async def beli_slash(self, interaction: discord.Interaction, item_id: str, jumlah: int = 1):
        await interaction.response.defer(ephemeral=True)
        hasil = self.bot.logic_handler._beli_logic(interaction.user.id, item_id, jumlah)
        await interaction.followup.send(hasil)

    @app_commands.command(name="gunakan", description="Menggunakan item dari inventaris.")
    @app_commands.describe(item_id="ID item yang ingin digunakan")
    async def gunakan_slash(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._gunakan_logic(interaction.user.id, item_id)
        await interaction.followup.send(f"{interaction.user.mention}, {hasil}")

    # --- PREFIX COMMANDS ---
    @commands.command(name="toko", aliases=["shop"])
    async def toko_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._toko_logic()
        if isinstance(hasil, discord.Embed):
            await ctx.send(embed=hasil)
        else:
            await ctx.send(hasil)

    @commands.command(name="inventaris", aliases=["inventory", "inv", "i"])
    async def inventaris_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._inventaris_logic(ctx.author.id, ctx.author.name, ctx.author.avatar.url)
        if isinstance(hasil, discord.Embed):
            await ctx.send(embed=hasil)
        else:
            await ctx.send(hasil)
            
    @commands.command(name="beli", aliases=["buy"])
    async def beli_prefix(self, ctx: commands.Context, item_id: str = None, jumlah: int = 1):
        if not item_id:
            await ctx.send("Gunakan format: `rbeli <id_item> <jumlah>`")
            return
        hasil = self.bot.logic_handler._beli_logic(ctx.author.id, item_id, jumlah)
        await ctx.send(f"{ctx.author.mention}, {hasil}")

    @commands.command(name="gunakan", aliases=["use"])
    async def gunakan_prefix(self, ctx: commands.Context, item_id: str = None):
        if not item_id:
            await ctx.send("Gunakan format: `rgunakan <id_item>`")
            return
        hasil = self.bot.logic_handler._gunakan_logic(ctx.author.id, item_id)
        await ctx.send(f"{ctx.author.mention}, {hasil}")
        
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, 'GUILD_ID', None)
    await bot.add_cog(
        Economy(bot),
        guild=discord.Object(id=guild_id) if guild_id else None
    )