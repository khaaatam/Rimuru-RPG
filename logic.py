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
        print("Data pemain, toko, monster, dan quest berhasil dimuat.")

    def load_data_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        print(f"Peringatan: file '{filename}' tidak ditemukan, membuat data kosong.")
        return {}

    def save_player_data(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.players, f, indent=4)

    # --- FUNGSI LOGIKA GAME INTI ---
    def calculate_xp_for_level(self, level):
        return 100 * level

    def _mulai_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.players:
            return "Anda sudah memiliki karakter!"
        else:
            self.players[user_id_str] = {
                "level": 1, "xp": 0, "gold": 10, "hp": 100, "max_hp": 100,
                "attack": 5, "defense": 2,
                "equipment": {"senjata": None, "armor": None},
                "last_daily": "2000-01-01 00:00:00.000000", "inventory": {},
                "active_quest": { "id": None, "progress": 0 }
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
        if user_id_str not in self.players:
            return None

        player_data = self.players[user_id_str]
        required_xp = self.calculate_xp_for_level(player_data['level'])
        total_stats = self._get_player_total_stats(user_id_str)
    
        embed = discord.Embed(
            title=f"Profil: {user_name}",
            color=discord.Color.from_str("#FADA5E") # Warna emas yang lebih lembut
        )
        embed.set_thumbnail(url=user_avatar_url)
    
    # --- BAGIAN YANG DIUBAH ---

    # Baris 1: Info Dasar
        embed.add_field(name="🌟 Level", value=player_data['level'], inline=True)
        embed.add_field(name="✨ XP", value=f"{player_data['xp']}/{required_xp}", inline=True)
        embed.add_field(name="💰 Gold", value=player_data['gold'], inline=True)
    
    # Baris 2: Atribut Pertarungan (digabung agar ringkas)
        embed.add_field(name="❤️ HP", value=f"{player_data['hp']}/{player_data.get('max_hp', 100)}", inline=True)
        embed.add_field(name="⚔️ Attack", value=total_stats['attack'], inline=True)
        embed.add_field(name="🛡️ Defense", value=total_stats['defense'], inline=True)

    # Baris 3: Perlengkapan (kategori baru)
        equipment = player_data.get('equipment', {})
        senjata_id = equipment.get('senjata')
        armor_id = equipment.get('armor') # Disiapkan untuk masa depan

        senjata_nama = self.SHOP_ITEMS.get(senjata_id, {}).get('nama_tampilan', 'Kosong') if senjata_id else 'Kosong'
        armor_nama = self.SHOP_ITEMS.get(armor_id, {}).get('nama_tampilan', 'Kosong') if armor_id else 'Kosong'
    
        embed.add_field(
            name="`Perlengkapan Terpasang`",
            value=f"🗡️ **Senjata**: {senjata_nama}\n🛡️ **Armor**: {armor_nama}",
            inline=False
        )
    # ---------------------------
    
        embed.set_footer(text=f"ID Pemain: {user_id_str}")
        return embed

    def _jelajah_logic(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return None
        gold_ditemukan = random.randint(5, 20)
        xp_didapat = random.randint(10, 25)
        self.players[user_id_str]['gold'] += gold_ditemukan
        self.players[user_id_str]['xp'] += xp_didapat
        pesan_hasil = f"Anda menjelajahi hutan dan mendapatkan **{gold_ditemukan} Gold** serta **{xp_didapat} XP**!"
        leveled_up, pesan_level_up = self._cek_level_up_logic(user_id_str)
        if leveled_up: pesan_hasil += pesan_level_up
        self.save_player_data()
        return pesan_hasil

    def _hunting_logic(self, user_id, zone_id=None):
        user_id_str = str(user_id)
        if user_id_str not in self.players: return None
        
        # --- 1. Logika Zona ---
        if not zone_id:
            zona_list = [f"- `{zid}` ({zinfo['nama_tampilan']})" for zid, zinfo in self.MONSTERS.get('zona', {}).items()]
            return "Anda harus memilih zona berburu. Zona tersedia:\n" + "\n".join(zona_list)

        zone_id = zone_id.lower()
        if zone_id not in self.MONSTERS.get('zona', {}):
            return "Zona tidak ditemukan."

        zona_info = self.MONSTERS['zona'][zone_id]
        player_level = self.players[user_id_str]['level']
        if player_level < zona_info['level_rekomendasi']:
            return f"Level Anda terlalu rendah untuk **{zona_info['nama_tampilan']}**. Level rekomendasi: {zona_info['level_rekomendasi']}."

        # --- 2. Persiapan Pertarungan ---
        if self.players[user_id_str]['hp'] <= 0: return "HP Anda terlalu rendah untuk berburu!"
        
        monster_id = random.choice(zona_info['monster_list'])
        monster = self.MONSTERS['monster_data'][monster_id].copy()
        monster_hp = monster['hp']
        player_stats = self._get_player_total_stats(user_id_str)
        player_hp = self.players[user_id_str]['hp']
        log = [f"Anda memasuki **{zona_info['nama_tampilan']}** dan bertemu **{monster['nama']}** {monster['emoji']}!"]

        # --- 3. Simulasi Pertarungan ---
        while player_hp > 0 and monster_hp > 0:
            damage_ke_monster = max(1, player_stats['attack'] - monster['defense'])
            monster_hp -= damage_ke_monster
            log.append(f"⚔️ Anda menyerang, **{damage_ke_monster}** damage. (HP Monster: {max(0, monster_hp)})")
            if monster_hp <= 0: break
            
            damage_ke_pemain = max(1, monster['attack'] - player_stats['defense'])
            player_hp -= damage_ke_pemain
            log.append(f"{monster['emoji']} Monster menyerang, **{damage_ke_pemain}** damage. (HP Anda: {max(0, player_hp)})")

        # --- 4. Hasil Pertarungan ---
        if player_hp > 0:
            gold = random.randint(*monster['hadiah_gold'])
            xp = random.randint(*monster['hadiah_xp'])
            self.players[user_id_str]['hp'] = player_hp
            self.players[user_id_str]['gold'] += gold
            self.players[user_id_str]['xp'] += xp
            log.append(f"\n**KEMENANGAN!** Sisa HP: **{player_hp}**. Anda mendapat **{gold} Gold** & **{xp} XP**.")

            # 4a. Peluang Item Drop (contoh: 15% drop ramuan)
            if random.random() < 0.15:
                item_drop_id = 'ramuan'
                inventory = self.players[user_id_str].get('inventory', {})
                inventory[item_drop_id] = inventory.get(item_drop_id, 0) + 1
                self.players[user_id_str]['inventory'] = inventory
                log.append(f"✨ Anda menemukan **Ramuan Kesehatan** dari monster!")

            # 4b. Cek Progres Quest
            pesan_quest = self._cek_quest_progress_logic(user_id_str, monster_id)
            if pesan_quest: log.append(pesan_quest)

            # 4c. Cek Level Up
            leveled_up, pesan_level_up = self._cek_level_up_logic(user_id_str)
            if leveled_up: log.append(pesan_level_up)
        else:
            self.players[user_id_str]['hp'] = 0
            gold_hilang = int(self.players[user_id_str]['gold'] * 0.10) # Kehilangan 10% gold
            self.players[user_id_str]['gold'] -= gold_hilang
            log.append(f"\n**KEKALAHAN!** Anda pingsan dan kehilangan **{gold_hilang} Gold**.")
        
        self.save_player_data()
        return "\n".join(log)

    def _cek_quest_progress_logic(self, user_id_str, monster_id):
        """Memeriksa dan mengupdate progres quest setelah pertarungan."""
        active_quest = self.players[user_id_str]['active_quest']
        if active_quest['id'] is not None:
            quest_info = self.QUESTS[active_quest['id']]
            if quest_info['target_monster'] == monster_id:
                active_quest['progress'] += 1
                if active_quest['progress'] >= quest_info['jumlah_target']:
                    hadiah_gold = quest_info['hadiah_gold']
                    hadiah_xp = quest_info['hadiah_xp']
                    self.players[user_id_str]['gold'] += hadiah_gold
                    self.players[user_id_str]['xp'] += hadiah_xp
                    self.players[user_id_str]['active_quest'] = {"id": None, "progress": 0}
                    return f"\n**QUEST SELESAI: {quest_info['nama']}!**\nHadiah: **{hadiah_gold} Gold** & **{hadiah_xp} XP**."
        return None # Tidak ada update quest

    def _cek_level_up_logic(self, user_id_str):
        player_level = self.players[user_id_str]['level']
        required_xp = self.calculate_xp_for_level(player_level)
        if self.players[user_id_str]['xp'] >= required_xp:
            self.players[user_id_str]['level'] += 1
            self.players[user_id_str]['xp'] -= required_xp
            self.players[user_id_str]['max_hp'] += 20
            self.players[user_id_str]['hp'] = self.players[user_id_str]['max_hp']
            return True, f"\n🎉 **SELAMAT!** Anda naik ke **Level {self.players[user_id_str]['level']}**!"
        return False, ""

    def _toko_logic(self):
        if not self.SHOP_ITEMS: return "Maaf, toko sedang kosong."
        embed = discord.Embed(title="🛒 Toko Item", description="Gunakan `rbeli <id_item> <jumlah>` untuk membeli.", color=discord.Color.green())
        for item_id, item_info in self.SHOP_ITEMS.items():
            embed.add_field(name=f"{item_info.get('emoji', '')} {item_info.get('nama_tampilan', 'Item')} - {item_info.get('harga', 0)} Gold", value=f"`ID: {item_id}` | {item_info.get('deskripsi', '')}", inline=False)
        return embed

    def _inventaris_logic(self, user_id, user_name, user_avatar_url):
        user_id_str = str(user_id)
        if user_id_str not in self.players or not self.players[user_id_str].get('inventory'): return "Inventaris Anda kosong."
        embed = discord.Embed(title=f"🎒 Inventaris - {user_name}", color=discord.Color.orange())
        embed.set_thumbnail(url=user_avatar_url)
        for item_id, jumlah in self.players[user_id_str]['inventory'].items():
            item_info = self.SHOP_ITEMS.get(item_id)
            if item_info: embed.add_field(name=f"{item_info.get('emoji', '')} {item_info.get('nama_tampilan', 'Item')}", value=f"Jumlah: **{jumlah}**", inline=True)
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
            pemulihan = efek['hp']
            self.players[user_id_str]['hp'] = min(self.players[user_id_str]['max_hp'], self.players[user_id_str]['hp'] + pemulihan)
            pesan_efek = f"HP Anda pulih sebesar **{pemulihan}**!"
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
        
    def _heal_logic(self, user_id):
        user_id_str = str(user_id)
        inventory = self.players[user_id_str].get('inventory', {})
        
        # Cari item ramuan di inventaris
        # Kita asumsikan ID itemnya adalah "ramuan"
        if 'ramuan' not in inventory or inventory['ramuan'] <= 0:
            return "Anda tidak memiliki Ramuan Kesehatan! Beli di `/toko`."

        # Ambil info item dari toko
        item_info = self.SHOP_ITEMS.get('ramuan')
        if not item_info:
            return "Terjadi kesalahan pada item ramuan."

        # Cek jika HP sudah penuh
        if self.players[user_id_str]['hp'] == self.players[user_id_str]['max_hp']:
            return "HP Anda sudah penuh."

        # Proses healing
        self.players[user_id_str]['hp'] = self.players[user_id_str]['max_hp']
        
        # Kurangi ramuan dari inventaris
        inventory['ramuan'] -= 1
        if inventory['ramuan'] <= 0:
            del inventory['ramuan']

        self.save_player_data()
        return f"Anda menggunakan **{item_info['nama_tampilan']}** dan HP Anda pulih sepenuhnya!"

    async def _leaderboard_logic(self, bot):
        if not self.players:
            return "Papan peringkat masih kosong karena belum ada pemain."

        # Mengurutkan pemain berdasarkan Level (tertinggi), lalu XP (tertinggi)
        sorted_players = sorted(
            self.players.items(),
            key=lambda item: (item[1].get('level', 0), item[1].get('xp', 0)),
            reverse=True
        )

        # Buat embed dasar
        embed = discord.Embed(
            title="🏆 Papan Peringkat Teratas",
            description="Berikut adalah 10 pemain dengan level tertinggi di server.",
            color=discord.Color.purple()
        )

        # Buat daftar peringkat
        leaderboard_text = ""
        for i, (user_id, data) in enumerate(sorted_players[:10]):
            try:
                # Ambil nama pengguna dari ID-nya
                user = await bot.fetch_user(int(user_id))
                user_name = user.display_name
            except discord.NotFound:
                user_name = "Pemain Tidak Dikenal"
            
            # Beri emoji untuk 3 besar
            rank_emoji = ["🥇", "🥈", "🥉"]
            if i < 3:
                rank = rank_emoji[i]
            else:
                rank = f"**#{i + 1}**"

            leaderboard_text += f"{rank} **{user_name}** - Level {data.get('level', 0)} ({data.get('xp', 0)} XP)\n"

        if not leaderboard_text:
            leaderboard_text = "Belum ada pemain yang bisa ditampilkan."

        embed.description = leaderboard_text
        return embed

    def _quests_list_logic(self):
        embed = discord.Embed(title="📜 Daftar Quest Tersedia", color=discord.Color.dark_teal())
        if not self.QUESTS:
            embed.description = "Tidak ada quest yang tersedia saat ini."
            return embed
        
        for quest_id, info in self.QUESTS.items():
            embed.add_field(
                name=f"{info['nama']} (`ID: {quest_id}`)",
                value=f"{info['deskripsi']}\n**Hadiah:** {info['hadiah_gold']} Gold, {info['hadiah_xp']} XP",
                inline=False
            )
        return embed

    def _quest_ambil_logic(self, user_id, quest_id):
        user_id_str = str(user_id)
        quest_id = quest_id.lower()

        if self.players[user_id_str]['active_quest']['id'] is not None:
            return "Anda sudah memiliki quest aktif! Selesaikan dulu."
        
        if quest_id not in self.QUESTS:
            return "Quest tidak ditemukan."
            
        self.players[user_id_str]['active_quest'] = {
            "id": quest_id,
            "progress": 0
        }
        self.save_player_data()
        return f"Anda telah mengambil quest: **{self.QUESTS[quest_id]['nama']}**."

    def _quest_info_logic(self, user_id):
        user_id_str = str(user_id)
        active_quest = self.players[user_id_str]['active_quest']

        if active_quest['id'] is None:
            return "Anda tidak memiliki quest aktif. Ambil satu dari `/quests`."
            
        quest_info = self.QUESTS[active_quest['id']]
        progress = active_quest['progress']
        target = quest_info['jumlah_target']

        embed = discord.Embed(
            title=f"Info Quest: {quest_info['nama']}",
            description=quest_info['deskripsi'],
            color=discord.Color.blue()
        )
        embed.add_field(name="Progres", value=f"**{progress} / {target}**")
        return embed
    
    def _zona_list_logic(self):
        embed = discord.Embed(title="🌍 Daftar Zona Hunting", color=discord.Color.dark_green())
        for zona_id, info in self.MONSTERS.get('zona', {}).items():
            embed.add_field(
            name=f"{info['nama_tampilan']} (`ID: {zona_id}`)",
            value=f"Rekomendasi Level: {info['level_rekomendasi']}",
            inline=False
            )
        return embed