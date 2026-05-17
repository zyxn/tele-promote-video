# Viral Telegram Bot

Bot Telegram untuk mengelola dan menjadwalkan posting media viral secara otomatis.

## Features

- 🤖 Auto-posting media ke channel
- 📅 Scheduler untuk posting otomatis
- 🖼️ Clickbait image generator
- 👥 Admin management system
- 📊 Database tracking dengan PostgreSQL
- 🔄 Verifikasi media sebelum posting

## Prerequisites

- Docker & Docker Compose
- Telegram Bot Token (dari [@BotFather](https://t.me/botfather))
- Telegram API credentials (dari [my.telegram.org](https://my.telegram.org))
- PostgreSQL database (Neon atau lainnya)

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Configure Environment Variables

Copy file `.env.example` ke `.env` dan isi dengan credentials Anda:

```bash
cp .env.example .env
```

Edit file `.env`:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# Telegram API Credentials
API_ID=your_api_id
API_HASH=your_api_hash

# Admin Configuration
ADMIN_IDS=123456789,987654321
ADMIN_GROUP_PRIVATE=-1001234567890
ADMIN_GROUP_PUBLIC=-1009876543210

# Channel Configuration
CHANNEL_PUBLIC=@your_public_channel
CHANNEL_PRIVATE=@your_private_channel

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Scheduler Configuration
POSTING_INTERVAL_MINUTES=60

# Nekos.best API Configuration
NEKOS_API_ENDPOINT=neko
```

### 3. Run with Docker

#### Build dan Start

```bash
docker-compose up -d --build
```

#### View Logs

```bash
docker-compose logs -f bot
```

#### Stop Bot

```bash
docker-compose down
```

#### Restart Bot

```bash
docker-compose restart bot
```

### 4. Run without Docker (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

## Docker Commands

### Build image

```bash
docker-compose build
```

### Start services

```bash
docker-compose up -d
```

### View logs

```bash
docker-compose logs -f
```

### Stop services

```bash
docker-compose down
```

### Restart services

```bash
docker-compose restart
```

### Remove all (including volumes)

```bash
docker-compose down -v
```

### Access container shell

```bash
docker-compose exec bot bash
```

## Project Structure

```
.
├── bot.py                  # Main bot entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker compose configuration
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment variables template
├── handlers/
│   ├── admin.py         # Admin command handlers
│   └── user.py          # User command handlers
├── services/
│   ├── media.py         # Media processing
│   ├── scheduler.py     # Auto-posting scheduler
│   └── verification.py  # Media verification
├── database/
│   ├── models.py        # Database models
│   └── crud.py          # Database operations
└── utils/
    ├── buttons.py       # Telegram inline buttons
    └── helpers.py       # Helper functions
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Token bot dari BotFather | Yes |
| `BOT_USERNAME` | Username bot | Yes |
| `API_ID` | Telegram API ID | Yes |
| `API_HASH` | Telegram API Hash | Yes |
| `ADMIN_IDS` | Comma-separated admin user IDs | Yes |
| `ADMIN_GROUP_PRIVATE` | Private admin group ID | Yes |
| `ADMIN_GROUP_PUBLIC` | Public admin group ID | Yes |
| `CHANNEL_PUBLIC` | Public channel username | Yes |
| `CHANNEL_PRIVATE` | Private channel username | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `POSTING_INTERVAL_MINUTES` | Auto-posting interval | No (default: 60) |
| `NEKOS_API_ENDPOINT` | Nekos.best API endpoint | No (default: neko) |

## Troubleshooting

### Bot tidak start

1. Check logs: `docker-compose logs -f bot`
2. Verify environment variables di `.env`
3. Pastikan database accessible

### Database connection error

1. Verify `DATABASE_URL` format
2. Check database server status
3. Verify network connectivity

### Permission errors

```bash
# Fix file permissions
chmod -R 755 .
```

## Security Notes

- ⚠️ **JANGAN** commit file `.env` ke git
- 🔒 Keep your bot token dan API credentials private
- 🛡️ Gunakan environment variables untuk sensitive data
- 🔐 Limit admin access dengan `ADMIN_IDS`

## License

MIT License

## Support

Untuk pertanyaan atau issues, silakan buka issue di repository ini.
