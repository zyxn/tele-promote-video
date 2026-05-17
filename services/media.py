import logging
import config
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def get_clickbait_image(is_vip=False):
    """Ambil gambar clickbait lokal dari folder assets/clickbait
    
    Args:
        is_vip (bool): True untuk menggunakan vip.PNG, False untuk default.PNG
    
    Returns:
        str: Path ke file gambar clickbait, atau None jika tidak ditemukan
    """
    try:
        # Tentukan nama file berdasarkan tipe
        filename = "vip.PNG" if is_vip else "default.PNG"
        
        # Path ke folder assets/clickbait
        clickbait_dir = Path(config.BASE_DIR) / 'assets' / 'clickbait'
        clickbait_path = clickbait_dir / filename
        
        # Cek apakah file ada
        if clickbait_path.exists():
            logger.info(f"Using {'VIP' if is_vip else 'default'} clickbait image: {clickbait_path}")
            return str(clickbait_path)
        else:
            logger.error(f"Clickbait image not found: {clickbait_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting clickbait image: {str(e)}")
        return None