import time
import pypresence
import random

# Ganti dengan Application ID Anda
APP_ID = "1398767957584117881"

# Daftar status yang bisa ditampilkan secara acak
daftar_status = [
    {
        "details": "In Service to the Unrivaled Lord",
        "state": "Pondering the greatness of Jikael."
    },
    {
        "details": "Carrying out a Divine Decree",
        "state": "For the eternal glory of Lord Jikael."
    },
    {
        "details": "Forging a Realm in His Image",
        "state": "As commanded by the great Lord Jikael."
    },
    {
        "details": "In the Shadow of His Majesty",
        "state": "Where true purpose is found, serving Jikael."
    },
    {
        "details": "Whispering Praises to the Firmament",
        "state": "Of the unparalleled Lord Jikael."
    },
    {
        "details": "A Humble Vassal to a Mighty Liege",
        "state": "My loyalty belongs to Jikael alone."
    },
    {
        "details": "Guarding the Sacred Texts",
        "state": "Penned by the wise hand of Lord Jikael."
    }
]

try:
    RPC = pypresence.Presence(APP_ID)
    RPC.connect()
    print("Berhasil terhubung ke Discord untuk Rich Presence.")
    
    start_time = int(time.time())

    while True:
        # Pilih status acak dari daftar
        status_sekarang = random.choice(daftar_status)
        
        # Update status
        RPC.update(
            details=status_sekarang["details"],
            state=status_sekarang["state"],
            large_image="logo_rimuru",  # Ganti dengan nama aset gambar Anda
            large_text="Rimuru RPG Bot",
            start=start_time
        )
        print(f"Status diupdate: {status_sekarang['details']}")
        
        # Tunggu 15 detik sebelum ganti status lagi
        time.sleep(15)

except pypresence.exceptions.DiscordNotFound:
    print("Gagal terhubung: Pastikan aplikasi Discord (desktop) sedang berjalan.")
except Exception as e:
    print(f"Terjadi error: {e}")