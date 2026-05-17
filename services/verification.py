from telethon import TelegramClient, errors
from telethon.tl.types import Channel
from telethon.tl.functions.channels import GetParticipantRequest
from config import CHANNELS
from typing import List
from telethon.tl.custom import Button
from utils.buttons import create_subscribe_buttons
import logging

logger = logging.getLogger(__name__)

async def check_user_subscriptions(client: TelegramClient, user_id: int) -> List[str]:
    """
    Cek channel apa saja yang belum di-subscribe user
    Menggunakan GetParticipantRequest untuk check membership yang lebih akurat
    """
    unsubscribed = []
    
    for name, channel in CHANNELS.items():
        # Skip channel publik dan private yang tidak perlu dicek
        if name in ['PUBLIC', 'PRIVATE']:
            continue
            
        try:
            # Gunakan GetParticipantRequest untuk mengecek membership
            await client(GetParticipantRequest(channel=channel, participant=user_id))
            logger.info(f"User {user_id} is subscribed to {channel}")
            
        except errors.UserNotParticipantError:
            # User belum join channel
            logger.info(f"User {user_id} is NOT subscribed to {channel}")
            unsubscribed.append(channel)
            
        except errors.ChatAdminRequiredError:
            # Bot tidak punya permission untuk cek participant
            logger.warning(f"Bot doesn't have permission to check participants in {channel}")
            # Assume user is not subscribed jika bot tidak bisa cek
            unsubscribed.append(channel)
            
        except errors.ChannelInvalidError:
            # Channel tidak valid atau tidak ditemukan
            logger.error(f"Invalid channel: {channel}")
            unsubscribed.append(channel)
            
        except ValueError as e:
            # Channel ID tidak valid
            logger.error(f"Invalid channel ID {channel}: {e}")
            unsubscribed.append(channel)
            
        except Exception as e:
            # Handle error lain yang mungkin terjadi
            logger.error(f"Unexpected error checking {channel}: {e}")
            unsubscribed.append(channel)
    
    return unsubscribed

async def is_user_subscribed_to_channel(client: TelegramClient, user_id: int, channel_id) -> bool:
    """
    Check if user is subscribed to a specific channel
    Returns True if subscribed, False otherwise
    """
    try:
        await client(GetParticipantRequest(channel=channel_id, participant=user_id))
        return True
        
    except errors.UserNotParticipantError:
        return False
        
    except (errors.ChatAdminRequiredError, errors.ChannelInvalidError, ValueError) as e:
        logger.warning(f"Error checking subscription for user {user_id} in channel {channel_id}: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error checking subscription: {e}")
        return False

async def validate_all_subscriptions(client: TelegramClient, user_id: int) -> dict:
    """
    Validate user subscription to all required channels
    Returns detailed information about subscription status
    """
    result = {
        'all_subscribed': True,
        'unsubscribed_channels': [],
        'subscription_details': {}
    }
    
    for name, channel in CHANNELS.items():
        if name in ['PUBLIC', 'PRIVATE']:
            continue
            
        is_subscribed = await is_user_subscribed_to_channel(client, user_id, channel)
        
        result['subscription_details'][name] = {
            'channel': channel,
            'subscribed': is_subscribed
        }
        
        if not is_subscribed:
            result['all_subscribed'] = False
            result['unsubscribed_channels'].append(channel)
    
    return result

async def send_subscription_request(event, missing_channels: List[str]):
    """
    Kirim pesan dengan button untuk subscribe
    Adapted to match your code style
    """
    if not missing_channels:
        return
        
    buttons = create_subscribe_buttons(missing_channels)
    
    message = "⚠️ **Untuk melanjutkan, silakan subscribe channel berikut:**\n\n"
    
    for i, channel in enumerate(missing_channels, 1):
        channel_clean = channel.lstrip('@')
        message += f"{i}. @{channel_clean}\n"
    
    message += "\nSetelah subscribe, klik tombol '✅ Sudah Subscribe' di bawah."
    
    await event.reply(
        message,
        buttons=buttons,
        parse_mode='markdown'
    )