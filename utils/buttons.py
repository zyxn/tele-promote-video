from telethon.tl.custom import Button

def create_subscribe_buttons(channels):
    """Buat button untuk subscribe channel"""
    buttons = []
    for channel in channels:
        # Remove @ if present and create proper URL
        channel_clean = channel.lstrip('@')
        buttons.append(
            [Button.url(f"Join {channel_clean}", f"https://t.me/{channel_clean}")]
        )
    buttons.append([Button.inline("✅ Sudah Subscribe", b'subscribed')])
    return buttons

