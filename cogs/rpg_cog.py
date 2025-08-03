import discord
from discord import app_commands
from discord.ext import commands

class RPG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Perintah utama yang baru, menggantikan /hunting dan /dungeon
    @app_commands.command(name="hunt", description="Berburu monster biasa (cooldown 1 menit).")
    async def hunt_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._hunt_logic(interaction.user.id)
        await interaction.followup.send(f"{interaction.user.mention}\n{hasil}")

    @commands.command(name="hunt", aliases=['h'])
    async def hunt_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._hunt_logic(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}\n{hasil}")
            
    @app_commands.command(name="jelajah", description="Berpetualang melawan elite boss (cooldown 1 jam).")
    async def jelajah_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._jelajah_logic(interaction.user.id)
        await interaction.followup.send(f"{interaction.user.mention}, {hasil}")
        
    @commands.command(name="jelajah", aliases=['adv'])
    async def jelajah_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._jelajah_logic(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}, {hasil}")

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        RPG(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )