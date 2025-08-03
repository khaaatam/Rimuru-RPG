import os
import json
import random
from datetime import datetime, timedelta
import discord

DB_FILE = "database.json"

class LogicHandler:
    def __init__(self):
        self.players = self.load_data_file("database.json")
        self.SHOP_ITEMS = self.load_data_file("shop.json")
        self.MONSTERS = self.load_data_file("monsters.json")
        self.QUESTS = self.load_data_file("quests.json")
        self.DUNGEONS = self.load_data_file("dungeons.json")
        self.LOOT_TABLES = self.load_data_file("loot_tables.json")
        self.ELITE_BOSSES = self.load_data_file("elite_bosses.json")
        print("Semua data berhasil dimuat.")

    def load_data_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        print(f"Peringatan: file '{filename}' tidak ditemukan, membuat data kosong.")
        return {}

    def save_player_data(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.players, f, indent=4)

    # --- FUNGSI LOGIKA INTI GAME ---
    
    def calculate_xp_for_level(self, level):
        return 100 * level

    def _cek_level_up_logic(self, user_id_str):
        player_data = self.players[user_id_str]
        player_level = player_data['level']
        required_xp = self.calculate_xp_for_level(player_level)
        if player_data['xp'] >= required_xp:
            player_data['level'] += 1
            player_data['xp'] -= required_xp
            player_data['max_hp'] += 20
            player_data['hp'] = player_data['max_hp']
            return True, f"\n🎉 **SELAMAT!** Anda naik ke **Level {player_data['level']}**!"
        return False, ""

    def _cek_quest_progress_logic(self, user_id_str, monster_id):
        active_quest = self.players[user_id_str].get('active_quest')
        if not active_quest or active_quest.get('id') is None:
            return None
        quest_info = self.QUESTS.get(active_quest['id'])
        if not quest_info or quest_info.get('target_monster') != monster_id:
            return None
        active_quest['progress'] = active_quest.get('progress', 0) + 1
        if active_quest['progress'] >= quest_info.get('jumlah_target', 999):
            hadiah_gold = quest_info.get('hadiah_gold', 0)
            hadiah_xp = quest_info.get('hadiah_xp', 0)
            self.players[user_id_str]['gold'] += hadiah_gold
            self.players[user_id_str]['xp'] += hadiah_xp
            self.players[user_id_str]['active_quest'] = {"id": None, "progress": 0}
            return f"\n**QUEST SELESAI: {quest_info['nama']}!** Hadiah: **{hadiah_gold} Gold** & **{hadiah_xp} XP**."
        # Mengembalikan pesan progres jika quest belum selesai
        return f"\n📜 Progres Quest: **{active_quest['progress']}/{quest_info['jumlah_target']}**."

    # --- LOGIKA KARAKTER & PROFIL ---

    def _mulai_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.players:
            return "Anda sudah memiliki karakter!"
        else:
            self.players[user_id_str] = {
                "level": 1, "xp": 0, "gold": 50, # <-- Gold awal ditambah
                "hp": 100, "max_hp": 100,
                "attack": 10, 
                "defense": 5,
                "equipment": {
                    "senjata": "pedang_pemula", 
                    "armor": None
                },
                "inventory": {}, 
                "dungeon_progress": {"unlocked": 1, "cooldown_until": "2000-01-01T00:00:00"},
                "hunt_cooldown_until": "2000-01-01T00:00:00",
                "jelajah_cooldown_until": "2000-01-01T00:00:00",
                "active_quest": {
                    "id": None, 
                    "progress": 0
                    },
                "last_daily": "2000-01-01T00:00:00.000000"
            }
        self.save_player_data()
        return "Selamat datang di dunia petualangan!"
    def _get_player_total_stats(self, user_id):
        user_id_str = str(user_id)
        player_data = self.players[user_id_str]
        total_stats = {"attack": player_data.get("attack", 0), "defense": player_data.get("defense", 0)}
        for slot, item_id in player_data.get("equipment", {}).items():
            if item_id:
                item_info = self.SHOP_ITEMS.get(item_id)
                if item_info and item_info.get('efek'):
                    for stat, value in item_info['efek'].items():
                        if stat in total_stats: total_stats[stat] += value
        return total_stats

    def _profil_logic(self, user_id, user_name, user_avatar_url):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return None
        player_data = self.players[user_id_str]
        required_xp = self.calculate_xp_for_level(player_data['level'])
        total_stats = self._get_player_total_stats(user_id_str)
        embed = discord.Embed(title=f"Profil: {user_name}", color=discord.Color.from_str("#FADA5E"))
        embed.set_thumbnail(url=user_avatar_url)
        embed.add_field(name="🌟 Level", value=player_data['level'], inline=True)
        embed.add_field(name="✨ XP", value=f"{player_data['xp']}/{required_xp}", inline=True)
        embed.add_field(name="💰 Gold", value=player_data['gold'], inline=True)
        embed.add_field(name="❤️ HP", value=f"{player_data['hp']}/{player_data.get('max_hp', 100)}", inline=True)
        embed.add_field(name="⚔️ Attack", value=total_stats['attack'], inline=True)
        embed.add_field(name="🛡️ Defense", value=total_stats['defense'], inline=True)
        embed.add_field(name=f"Dungeon {player_data['dungeon_progress']['current_dungeon']}", value=f"Monsters Defeated: {player_data['dungeon_progress']['monsters_defeated']}", inline=True)
        equipment = player_data.get('equipment', {})
        senjata_id = equipment.get('senjata')
        armor_id = equipment.get('armor')
        senjata_nama = self.SHOP_ITEMS.get(senjata_id, {}).get('nama_tampilan', 'Kosong') if senjata_id else 'Kosong'
        armor_nama = self.SHOP_ITEMS.get(armor_id, {}).get('nama_tampilan', 'Kosong') if armor_id else 'Kosong'
        embed.add_field(name="`Perlengkapan Terpasang`", value=f"🗡️ **Senjata**: {senjata_nama}\n🛡️ **Armor**: {armor_nama}", inline=False)
        embed.set_footer(text=f"ID Pemain: {user_id_str}")
        return embed

    # --- LOGIKA AKSI RPG ---

    def _generic_fight_logic(self, player_hp, player_stats, monster):
        monster_hp = monster['hp']
        log = []
        while player_hp > 0 and monster_hp > 0:
            damage_ke_monster = max(1, player_stats['attack'] - monster['defense'])
            monster_hp -= damage_ke_monster
            log.append(f"⚔️ Anda menyerang, **{damage_ke_monster}** damage.")
            if monster_hp <= 0: break
            damage_ke_pemain = max(1, monster['attack'] - player_stats['defense'])
            player_hp -= damage_ke_pemain
            log.append(f"{monster['emoji']} Monster menyerang, **{damage_ke_pemain}** damage.")
        return player_hp, log

    def _hunt_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return "Anda belum membuat karakter!"
        player_data = self.players[user_id_str]

        cooldown = datetime.fromisoformat(player_data.get("hunt_cooldown_until", "2000-01-01T00:00:00"))
        if datetime.now() < cooldown:
            sisa_detik = int((cooldown - datetime.now()).total_seconds())
            return f"Anda baru saja berburu! Coba lagi dalam **{sisa_detik} detik**."

        if player_data['hp'] <= 0: return "HP Anda terlalu rendah!"
        
        dungeon_id = str(player_data['dungeon_progress'].get('unlocked', 1))
        dungeon_info = self.DUNGEONS[dungeon_id]
        monster_id = random.choice(dungeon_info['regular_monsters'])
        monster = self.MONSTERS['monster_data'][monster_id].copy()

        player_hp_final, log_pertarungan = self._generic_fight_logic(player_data['hp'], self._get_player_total_stats(user_id_str), monster)
        log = [f"**{dungeon_info['nama']}** | Anda bertemu **{monster['nama']}** {monster['emoji']}!"] + log_pertarungan

        if player_hp_final > 0:
            player_data['hp'] = player_hp_final
            gold = random.randint(*monster['hadiah_gold'])
            xp = random.randint(*monster['hadiah_xp'])
            player_data['gold'] += gold
            player_data['xp'] += xp
            log.append(f"\n**KEMENANGAN!** Anda mendapat **{gold} Gold** & **{xp} XP**.")
            
            pesan_drop = self._cek_item_drop_logic(user_id_str, monster_id, 'regular_monsters')
            if pesan_drop: log.append(pesan_drop)
            
            pesan_quest = self._cek_quest_progress_logic(user_id_str, monster_id)
            if pesan_quest: log.append(pesan_quest)
            
            leveled_up, pesan_level_up = self._cek_level_up_logic(user_id_str)
            if leveled_up: log.append(pesan_level_up)
        else:
            player_data['hp'] = 0
            log.append("\n**KEKALAHAN!** HP Anda menjadi 0.")

        player_data['hunt_cooldown_until'] = (datetime.now() + timedelta(minutes=1)).isoformat()
        self.save_player_data()
        return "\n".join(log)

    def _jelajah_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return "Anda belum membuat karakter!"
        player_data = self.players[user_id_str]

        cooldown = datetime.fromisoformat(player_data.get("jelajah_cooldown_until", "2000-01-01T00:00:00"))
        if datetime.now() < cooldown:
            sisa_waktu = cooldown - datetime.now()
            jam, sisa = divmod(int(sisa_waktu.total_seconds()), 3600)
            menit, _ = divmod(sisa, 60)
            return f"Anda baru saja berpetualang! Coba lagi dalam **{jam} jam {menit} menit**."

        if player_data['hp'] <= 0: return "HP Anda terlalu rendah!"

        dungeon_id = str(player_data['dungeon_progress']['unlocked'])
        dungeon_key = f"dungeon_{dungeon_id}"
        if dungeon_key not in self.ELITE_BOSSES: return "Tidak ada elite boss di dungeon ini."
            
        elite_boss_info = random.choice(self.ELITE_BOSSES[dungeon_key])
        monster_id = elite_boss_info['id']
        monster = self.MONSTERS['monster_data'][monster_id].copy()

        player_hp_final, log_pertarungan = self._generic_fight_logic(player_data['hp'], self._get_player_total_stats(user_id_str), monster)
        log = [f"Dalam petualangan Anda, **{monster['nama']}** {monster['emoji']} muncul!"] + log_pertarungan
        
        if player_hp_final > 0:
            player_data['hp'] = player_hp_final
            gold = random.randint(*monster['hadiah_gold'])
            xp = random.randint(*monster['hadiah_xp'])
            player_data['gold'] += gold
            player_data['xp'] += xp
            log.append(f"\n**KEMENANGAN!** Anda mengalahkan elite boss dan mendapat **{gold} Gold** serta **{xp} XP**.")
            
            pesan_drop = self._cek_item_drop_logic(user_id_str, monster_id, 'elite_bosses')
            if pesan_drop: log.append(pesan_drop)

            leveled_up, pesan_level_up = self._cek_level_up_logic(user_id_str)
            if leveled_up: log.append(pesan_level_up)
        else:
            player_data['hp'] = 0
            log.append("\n**KEKALAHAN!** Anda dikalahkan oleh elite boss.")

        player_data['jelajah_cooldown_until'] = (datetime.now() + timedelta(hours=1)).isoformat()
        self.save_player_data()
        return "\n".join(log)

    def _dungeon_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return "Anda belum membuat karakter!"
        player_data = self.players[user_id_str]
        dungeon_progress = player_data['dungeon_progress']

        cooldown = datetime.fromisoformat(dungeon_progress['cooldown_until'])
        if datetime.now() < cooldown:
            sisa_waktu = cooldown - datetime.now()
            jam, sisa = divmod(int(sisa_waktu.total_seconds()), 3600)
            menit, _ = divmod(sisa, 60)
            return f"Anda baru saja menyelesaikan dungeon! Coba lagi dalam **{jam} jam {menit} menit**."

        if player_data['hp'] <= 0: return "HP Anda terlalu rendah!"

        dungeon_id = str(dungeon_progress['unlocked'])
        if dungeon_id not in self.DUNGEONS: return "Selamat! Anda telah menyelesaikan semua dungeon."
            
        dungeon_info = self.DUNGEONS[dungeon_id]
        monster_id = dungeon_info['final_boss_id']
        monster = self.MONSTERS['monster_data'][monster_id].copy()

        player_hp_final, log_pertarungan = self._generic_fight_logic(player_data['hp'], self._get_player_total_stats(user_id_str), monster)
        log = [f"Anda menantang Final Boss: **{monster['nama']}** {monster['emoji']}!"] + log_pertarungan

        if player_hp_final > 0:
            player_data['hp'] = player_hp_final
            hadiah = dungeon_info['hadiah_boss']
            player_data['gold'] += hadiah['gold']
            player_data['xp'] += hadiah['xp']
            log.append(f"\n**BOSS DIKALAHKAN!** Hadiah: **{hadiah['gold']} Gold** & **{hadiah['xp']} XP**.")
            
            pesan_drop = self._cek_item_drop_logic(user_id_str, monster_id, 'dungeon_bosses')
            if pesan_drop: log.append(pesan_drop)
            
            dungeon_progress['unlocked'] += 1
            
            leveled_up, pesan_level_up = self._cek_level_up_logic(user_id_str)
            if leveled_up: log.append(pesan_level_up)
        else:
            player_data['hp'] = 0
            log.append("\n**KEKALAHAN!** Anda gagal mengalahkan final boss.")
            
        dungeon_progress['cooldown_until'] = (datetime.now() + timedelta(hours=6)).isoformat()
        self.save_player_data()
        return "\n".join(log)


    def _heal_logic(self, user_id):
        user_id_str = str(user_id)
        inventory = self.players[user_id_str].get('inventory', {})
        if 'ramuan' not in inventory or inventory['ramuan'] <= 0:
            return "Anda tidak memiliki Ramuan Kesehatan! Beli di `/toko`."
        item_info = self.SHOP_ITEMS.get('ramuan')
        if not item_info: return "Terjadi kesalahan pada item ramuan."
        if self.players[user_id_str]['hp'] == self.players[user_id_str]['max_hp']:
            return "HP Anda sudah penuh."
        self.players[user_id_str]['hp'] = self.players[user_id_str]['max_hp']
        inventory['ramuan'] -= 1
        if inventory['ramuan'] <= 0: del inventory['ramuan']
        self.save_player_data()
        return f"Anda menggunakan **{item_info['nama_tampilan']}** dan HP Anda pulih sepenuhnya!"
    
    def _cek_item_drop_logic(self, user_id_str, monster_id, monster_type):
        loot_table = self.LOOT_TABLES.get(monster_type, {}).get(monster_id, {})
        
        if not loot_table:
            return None # Tidak ada drop untuk monster ini

        for item_id, chance in loot_table.items():
            if random.random() < chance:
                # Tambahkan item ke inventaris
                inventory = self.players[user_id_str].get('inventory', {})
                inventory[item_id] = inventory.get(item_id, 0) + 1
                self.players[user_id_str]['inventory'] = inventory
                
                # --- BAGIAN YANG DIPERBAIKI ---
                # 1. Ambil seluruh info item terlebih dahulu
                item_info = self.SHOP_ITEMS.get(item_id, {})
                # 2. Ambil emoji dan nama secara terpisah
                item_emoji = item_info.get('emoji', '')
                item_name = item_info.get('nama_tampilan', item_id)
                # 3. Gabungkan dalam pesan
                return f"✨ Anda mendapatkan: {item_emoji} **{item_name}**!"
                # ---------------------------
        
        return None # Tidak ada item yang drop kali ini
    
    # --- LOGIKA EKONOMI & ITEM ---
    
    def _toko_logic(self):
        if not self.SHOP_ITEMS: return "Maaf, toko sedang kosong."
        embed = discord.Embed(title="🛒 Toko Item", description="Gunakan `rbeli <id_item> [jumlah]` untuk membeli.", color=discord.Color.green())
        for item_id, item_info in self.SHOP_ITEMS.items():
            embed.add_field(name=f"{item_info.get('emoji', '')} {item_info.get('nama_tampilan', 'Item')} - {item_info.get('harga', 0)} Gold", value=f"`ID: {item_id}` | {item_info.get('deskripsi', '')}", inline=False)
        return embed

    def _inventaris_logic(self, user_id, user_name, user_avatar_url):
        user_id_str = str(user_id)
        
        # Buat embed dasar dengan gaya baru
        embed = discord.Embed(
            color=discord.Color.from_str("#2C2F33") # Warna abu-abu gelap
        )
        embed.set_author(name=f"{user_name} — inventory", icon_url=user_avatar_url)

        if user_id_str not in self.players or not self.players[user_id_str].get('inventory'):
            embed.description = "Inventaris Anda kosong."
            return embed

        inventory = self.players[user_id_str]['inventory']
        
        # 1. Kelompokkan item berdasarkan kategori
        kategori_items = {}
        for item_id, jumlah in inventory.items():
            item_info = self.SHOP_ITEMS.get(item_id)
            if item_info:
                kategori = item_info.get('kategori', 'Lain-lain')
                if kategori not in kategori_items:
                    kategori_items[kategori] = []
                
                emoji = item_info.get('emoji', '')
                nama = item_info.get('nama_tampilan', 'Item Tidak Dikenal')
                kategori_items[kategori].append(f"{emoji} {nama}: **{jumlah}**")

        # 2. Bagi kategori menjadi dua kolom
        kolom1_text = ""
        kolom2_text = ""
        kategori_terurut = sorted(kategori_items.keys())
        
        for i, kategori in enumerate(kategori_terurut):
            # Format teks untuk satu kategori penuh
            kategori_text = f"\n**{kategori}**\n" + "\n".join(kategori_items[kategori]) + "\n"
            
            # Bagi ke kolom kiri dan kanan secara seimbang
            if len(kolom1_text) <= len(kolom2_text):
                kolom1_text += kategori_text
            else:
                kolom2_text += kategori_text

        # 3. Tambahkan teks ke field embed
        if kolom1_text:
            embed.add_field(name="\u200b", value=kolom1_text, inline=True) # \u200b adalah spasi kosong
        if kolom2_text:
            embed.add_field(name="\u200b", value=kolom2_text, inline=True)
        
        return embed

    def _beli_logic(self, user_id, item_id, jumlah):
        user_id_str, item_id = str(user_id), item_id.lower()
        if item_id not in self.SHOP_ITEMS: return "Item tidak ditemukan."
        item_info = self.SHOP_ITEMS[item_id]
        total_harga = item_info['harga'] * jumlah
        if self.players[user_id_str]['gold'] < total_harga: return f"Gold Anda tidak cukup! Butuh **{total_harga} Gold**."
        self.players[user_id_str]['gold'] -= total_harga
        inventory = self.players[user_id_str].get('inventory', {})
        inventory[item_id] = inventory.get(item_id, 0) + jumlah
        self.players[user_id_str]['inventory'] = inventory
        self.save_player_data()
        return f"Anda berhasil membeli **{jumlah}x {item_info['nama_tampilan']}**."

    def _gunakan_logic(self, user_id, item_id):
        user_id_str, item_id = str(user_id), item_id.lower()
        inventory = self.players[user_id_str].get('inventory', {})
        if item_id not in inventory or inventory[item_id] <= 0: return "Anda tidak memiliki item tersebut."
        item_info = self.SHOP_ITEMS.get(item_id)
        if not item_info or not item_info.get('efek'): return "Item ini tidak bisa digunakan."
        efek, pesan_efek = item_info['efek'], ""
        if 'hp' in efek:
            heal_amount = efek['hp']
            if heal_amount == "full":
                self.players[user_id_str]['hp'] = self.players[user_id_str]['max_hp']
                pesan_efek = "HP Anda pulih sepenuhnya!"
            elif isinstance(heal_amount, int):
                self.players[user_id_str]['hp'] = min(self.players[user_id_str]['max_hp'], self.players[user_id_str]['hp'] + heal_amount)
                pesan_efek = f"HP Anda pulih sebesar **{heal_amount}**!"
        inventory[item_id] -= 1
        if inventory[item_id] <= 0: del inventory[item_id]
        self.save_player_data()
        return f"Anda menggunakan **{item_info['nama_tampilan']}**. {pesan_efek}"

    def _equip_logic(self, user_id, item_id):
        user_id_str, item_id = str(user_id), item_id.lower()
        inventory = self.players[user_id_str].get('inventory', {})
        if item_id not in inventory or inventory[item_id] <= 0: return "Anda tidak memiliki item tersebut."
        item_info = self.SHOP_ITEMS.get(item_id)
        if not item_info or 'tipe' not in item_info: return "Item ini tidak bisa dipakai."
        item_type = item_info['tipe']
        if item_type not in ['senjata', 'armor']: return f"**{item_info['nama_tampilan']}** bukan perlengkapan."
        item_lama_id = self.players[user_id_str]['equipment'].get(item_type)
        if item_lama_id: inventory[item_lama_id] = inventory.get(item_lama_id, 0) + 1
        inventory[item_id] -= 1
        if inventory[item_id] <= 0: del inventory[item_id]
        self.players[user_id_str]['equipment'][item_type] = item_id
        self.save_player_data()
        return f"Anda berhasil memakai **{item_info['nama_tampilan']}**."

    # --- LOGIKA QUEST ---
    
    def _quests_list_logic(self):
        embed = discord.Embed(title="📜 Daftar Quest Tersedia", color=discord.Color.dark_teal())
        if not self.QUESTS:
            embed.description = "Tidak ada quest yang tersedia saat ini."
            return embed
        for quest_id, info in self.QUESTS.items():
            embed.add_field(name=f"{info['nama']} (`ID: {quest_id}`)", value=f"{info['deskripsi']}\n**Hadiah:** {info['hadiah_gold']} Gold, {info['hadiah_xp']} XP", inline=False)
        return embed

    def _quest_ambil_logic(self, user_id, quest_id):
        user_id_str, quest_id = str(user_id), quest_id.lower()
        if self.players[user_id_str]['active_quest']['id'] is not None:
            return "Anda sudah memiliki quest aktif! Selesaikan dulu."
        if quest_id not in self.QUESTS: return "Quest tidak ditemukan."
        self.players[user_id_str]['active_quest'] = {"id": quest_id, "progress": 0}
        self.save_player_data()
        return f"Anda telah mengambil quest: **{self.QUESTS[quest_id]['nama']}**."

    def _quest_info_logic(self, user_id):
        user_id_str = str(user_id)
        active_quest = self.players[user_id_str]['active_quest']
        if active_quest['id'] is None: return "Anda tidak memiliki quest aktif."
        quest_info = self.QUESTS[active_quest['id']]
        progress = active_quest['progress']
        target = quest_info['jumlah_target']
        embed = discord.Embed(title=f"Info Quest: {quest_info['nama']}", description=quest_info['deskripsi'], color=discord.Color.blue())
        embed.add_field(name="Progres", value=f"**{progress} / {target}**")
        return embed
    
    # --- LOGIKA SOSIAL & UTILITAS ---
    
    def _harian_logic(self, user_id):
        user_id_str = str(user_id)
        last_claim_str = self.players[user_id_str].get("last_daily", "2000-01-01 00:00:00.000000")
        last_claim_time = datetime.fromisoformat(last_claim_str)
        if datetime.now() > last_claim_time + timedelta(hours=22):
            hadiah = 100
            self.players[user_id_str]['gold'] += hadiah
            self.players[user_id_str]['last_daily'] = datetime.now().isoformat()
            self.save_player_data()
            return f"Anda mengklaim hadiah harian sebesar **{hadiah} Gold**!"
        else:
            waktu_tunggu = (last_claim_time + timedelta(hours=22)) - datetime.now()
            jam, menit = divmod(waktu_tunggu.seconds // 60, 60)
            return f"Coba lagi dalam **{jam} jam {menit} menit**."

    async def _leaderboard_logic(self, bot):
        if not self.players: return "Papan peringkat masih kosong."
        sorted_players = sorted(self.players.items(), key=lambda item: (item[1].get('level', 0), item[1].get('xp', 0)), reverse=True)
        embed = discord.Embed(title="🏆 Papan Peringkat Teratas", description="10 pemain dengan level tertinggi.", color=discord.Color.purple())
        leaderboard_text = ""
        for i, (user_id, data) in enumerate(sorted_players[:10]):
            try:
                user = await bot.fetch_user(int(user_id))
                user_name = user.display_name
            except discord.NotFound:
                user_name = "Pemain Tidak Dikenal"
            rank_emoji = ["🥇", "🥈", "🥉"]
            rank = rank_emoji[i] if i < 3 else f"**#{i + 1}**"
            leaderboard_text += f"{rank} **{user_name}** - Level {data.get('level', 0)} ({data.get('xp', 0)} XP)\n"
        embed.description = leaderboard_text if leaderboard_text else "Belum ada pemain yang bisa ditampilkan."
        return embed