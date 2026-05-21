from telethon.tl.custom import Button

def create_subscribe_buttons(channels, video_id=None):
    """Buat button untuk subscribe channel"""
    buttons = []
    for channel in channels:
        # Remove @ if present and create proper URL
        channel_clean = channel.lstrip('@')
        buttons.append(
            [Button.url(f"Join {channel_clean}", f"https://t.me/{channel_clean}")]
        )
    callback_data = f'subscribed:{video_id}'.encode() if video_id else b'subscribed'
    buttons.append([Button.inline("✅ Sudah Subscribe", callback_data)])
    return buttons

