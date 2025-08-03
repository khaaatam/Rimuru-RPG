import discord
from discord import app_commands
from discord.ext import commands

class Dungeon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- SLASH COMMAND HANDLER ---
    @app_commands.command(name="dungeon", description="Masuki dungeon untuk melawan boss dan dapatkan hadiah besar.")
    async def dungeon_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hasil = self.bot.logic_handler._dungeon_logic(interaction.user.id)
        await interaction.followup.send(f"{interaction.user.mention}\n{hasil}")

    # --- PREFIX COMMAND HANDLER ---
    @commands.command(name="dungeon", aliases=['d'])
    async def dungeon_prefix(self, ctx: commands.Context):
        hasil = self.bot.logic_handler._dungeon_logic(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}\n{hasil}")

# --- FUNGSI SETUP ---
async def setup(bot: commands.Bot):
    guild_id = getattr(bot, "GUILD_ID", None)
    await bot.add_cog(
        Dungeon(bot),
        guild=discord.Object(id=int(guild_id)) if guild_id else None
    )