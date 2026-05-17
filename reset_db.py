"""
Script untuk mereset database
Menghapus semua data dan membuat ulang tabel
"""
from database.models import create_db_and_tables

if __name__ == '__main__':
    print("⚠️  PERINGATAN: Ini akan menghapus SEMUA data di database!")
    confirm = input("Ketik 'YES' untuk melanjutkan: ")
    
    if confirm == 'YES':
        print("Mereset database...")
        create_db_and_tables()
        print("✅ Database berhasil direset!")
    else:
        print("❌ Reset dibatalkan")
