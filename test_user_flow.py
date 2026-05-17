"""
Test script untuk mensimulasikan user flow
Gunakan ini untuk test apakah bot merespons dengan benar
"""
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH

async def test_start_command():
    """Test /start command dengan video ID"""
    
    # Ganti dengan nomor telepon Anda untuk testing
    phone = input("Masukkan nomor telepon (dengan kode negara, contoh: +628123456789): ")
    
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        await client.start(phone=phone)
        print("✅ Client connected!")
        
        # Ganti dengan username bot Anda
        bot_username = 'FWLMedia_Bot'
        
        # Test 1: /start tanpa parameter
        print("\n=== Test 1: /start tanpa parameter ===")
        await client.send_message(bot_username, '/start')
        await asyncio.sleep(2)
        
        # Test 2: /start dengan video ID (ganti dengan ID yang valid dari database)
        video_id = input("\nMasukkan video ID untuk test (atau tekan Enter untuk skip): ")
        if video_id:
            print(f"\n=== Test 2: /start dengan video ID {video_id} ===")
            await client.send_message(bot_username, f'/start {video_id}')
            await asyncio.sleep(2)
        
        print("\n✅ Test selesai! Cek log bot untuk melihat detail.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(test_start_command())
