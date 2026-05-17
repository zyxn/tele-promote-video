from config import BOT_USERNAME
from urllib.parse import quote

def create_video_caption(video) -> str:
    """Buat caption untuk postingan di channel publik"""
    return (
        f"{video.title}\n\n"
        f"t.me/{BOT_USERNAME}?start={video.random_id}\n"
    )

def format_channel_name(channel_entity):
    """Format nama channel untuk display"""
    if hasattr(channel_entity, 'title'):
        return channel_entity.title
    return str(channel_entity)