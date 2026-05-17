"""
Test script untuk scheduler posting
Jalankan: python test_scheduler.py
"""

from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN
from services.scheduler import post_video_to_public
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_posting():
    client = TelegramClient('viral_bot', API_ID, API_HASH)
    
    try:
        await client.start(bot_token=BOT_TOKEN)
        logger.info("Bot connected!")
        
        logger.info("Testing post_video_to_public function...")
        await post_video_to_public(client)
        
        logger.info("Test completed!")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}", exc_info=True)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_posting())
