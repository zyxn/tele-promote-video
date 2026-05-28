import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'FWLMedia_Bot')

# Admin Configuration
ADMIN_GROUPS = {
    'PRIVATE': int(os.getenv('ADMIN_GROUP_PRIVATE', '-1005235421278')),
    'PUBLIC': int(os.getenv('ADMIN_GROUP_PUBLIC', '-1003744094091'))
}

# Parse ADMIN_IDS from comma-separated string
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Telegram API
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

# Channel Configuration
CHANNELS = {
    'PUBLIC': os.getenv('CHANNEL_PUBLIC', '@fwlheavens'),
    'PRIVATE': os.getenv('CHANNEL_PRIVATE', '@ayam_goreng_rasa_bakwan'),
    'ch1': os.getenv('CHANNEL_CH1', '@fwlbasechat'),
}

# Add optional channels if they exist in environment
if os.getenv('CHANNEL_CH2'):
    CHANNELS['ch2'] = os.getenv('CHANNEL_CH2')
if os.getenv('CHANNEL_CH3'):
    CHANNELS['ch3'] = os.getenv('CHANNEL_CH3')
if os.getenv('CHANNEL_CH4'):
    CHANNELS['ch4'] = os.getenv('CHANNEL_CH4')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')

# VIP Group Chat - Forward VIP content here
VIP_GROUP_CHAT = os.getenv('VIP_GROUP_CHAT')

# Paths
BASE_DIR = Path(__file__).parent

# Scheduler
POSTING_INTERVAL_MINUTES = int(os.getenv('POSTING_INTERVAL_MINUTES', '60'))

# Nekos.best API Configuration
# Endpoints yang tersedia:
# SFW: neko, waifu, husbando, kitsune, etc.
# Dokumentasi: https://docs.nekos.best/
NEKOS_API_ENDPOINT = os.getenv('NEKOS_API_ENDPOINT', 'neko')