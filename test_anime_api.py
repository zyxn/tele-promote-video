"""
Test script untuk anime-api integration
Jalankan: python test_anime_api.py
"""

from services.media import get_random_clickbait_image

def test_api():
    print("🧪 Testing anime-api integration...")
    print("=" * 50)
    
    # Test get 1 NSFW image
    print("\n📸 Fetching 1 NSFW image from API...")
    image_url = get_random_clickbait_image()
    
    if image_url:
        print(f"✅ Success! Got image URL:")
        print(f"🔗 {image_url}")
        print("\n✨ API integration working correctly!")
    else:
        print("❌ Failed to get image from API")
        print("Check your internet connection and anime-api installation")
    
    print("=" * 50)

if __name__ == "__main__":
    test_api()
