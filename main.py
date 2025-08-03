import discord
from discord.ext import commands
import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio

from logic import LogicHandler

# --- KONFIGURASI & SETUP AWAL ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

DB_FILE = "database.json"


# --- SETUP BOT DENGAN KELAS KUSTOM ---
class RimuruBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.GUILD_ID = GUILD_ID
        self.logic_handler = LogicHandler()

    async def setup_hook(self):
        """Ini adalah tempat untuk semua setup asinkron."""
        # 1. Memuat semua Cogs
        print("Memuat Cogs...")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"- Cog '{filename[:-3]}' berhasil dimuat.")
                except Exception as e:
                    print(f"- Gagal memuat cog '{filename[:-3]}': {e}")
        
        # 2. Sinkronisasi slash commands
        print("\nSinkronisasi slash commands...")
        try:
            if self.GUILD_ID:
                guild_obj = discord.Object(id=int(self.GUILD_ID))
                await self.tree.sync(guild=guild_obj)
                print("Slash commands berhasil disinkronkan ke server.")
            else:
                await self.tree.sync()
                print("Slash commands berhasil disinkronkan secara global.")
        except Exception as e:
            print(f"Gagal sinkronisasi slash commands: {e}")

intents = discord.Intents.default()
intents.message_content = True
bot = RimuruBot(command_prefix=['r!', 'rmr '], case_insensitive=True, intents=intents, help_command=None)
bot.activity = discord.Activity(type=discord.ActivityType.watching, name="Rimuru | r!help")

@bot.event
async def on_ready():
    print("====================================")
    print(f"Bot {bot.user} (prefix: '{bot.command_prefix}') telah online!")
    print("====================================")

# --- MENJALANKAN BOT ---
if __name__ == "__main__":
    if TOKEN is None:
        print("Error: Token tidak ditemukan di file .env")
    else:
        bot.run(TOKEN)