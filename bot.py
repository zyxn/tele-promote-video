from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN
from handlers import user, admin
from services.scheduler import setup_scheduler
import logging
import sys

# Configure logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set stdout encoding to UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

async def main():
    client = TelegramClient('viral_bot', API_ID, API_HASH)
    
    try:
        await client.start(bot_token=BOT_TOKEN)
        logger.info("Bot started successfully!")
        
        # Setup handlers
        await user.setup_user_handlers(client)
        await admin.setup_admin_handlers(client)
        
        # Setup scheduler
        setup_scheduler(client)
        
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())