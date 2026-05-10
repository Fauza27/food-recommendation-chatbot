import pandas as pd
import numpy as np

def create_examples():
    # 1. Chatbot Food Dataset Example
    print("Creating example for chatbot_food_dataset.csv...")
    try:
        df_final = pd.read_csv('data/chatbot_food_dataset.csv', nrows=3)
        
        # Mock data for privacy
        df_final['nama_tempat'] = ['Warung Makan Contoh', 'Kafe Simulasi Asik', 'Resto Dummy Enak']
        df_final['lokasi'] = ['Jl. Contoh No. 123, Jakarta Selatan', 'Jl. Simulasi No. 45, Bandung', 'Jl. Dummy No. 88, Surabaya']
        df_final['kategori_makanan'] = ['Nusantara, Seafood', 'Kopi, Roti', 'Western, Steak']
        df_final['range_harga'] = ['Rp 20.000 - Rp 50.000', 'Rp 15.000 - Rp 40.000', 'Rp 100.000 - Rp 250.000']
        df_final['menu_andalan'] = ['Nasi Goreng Spesial, Gurame Bakar', 'Kopi Susu Gula Aren, Croissant', 'Sirloin Steak, Mashed Potato']
        df_final['link_lokasi'] = ['https://maps.google.com/?q=contoh1', 'https://maps.google.com/?q=contoh2', 'https://maps.google.com/?q=contoh3']
        
        if 'caption' in df_final.columns:
            df_final['caption'] = [
                'Ini adalah contoh caption 1 yang merepresentasikan postingan makanan lokal.',
                'Suasana kafe simulasi ini cocok untuk nongkrong dan nugas santai.',
                'Menikmati steak dengan tingkat kematangan medium rare di resto dummy.'
            ]
            
        if 'cleaned_transcribe' in df_final.columns:
            df_final['cleaned_transcribe'] = [
                'hari ini kita mau cobain warung contoh yang katanya sambalnya mantap banget harganya juga murah meriah',
                'tempatnya asik banget buat kerja wifi kenceng kopinya juga berasa',
                'wah dagingnya juicy banget saus mushroomnya juara'
            ]
            
        if 'ownerUsername' in df_final.columns:
            df_final['ownerUsername'] = ['foodvlogger_contoh', 'cafe_hunter_dummy', 'steak_lover_sim']
            
        df_final.to_csv('data/example_chatbot_dataset.csv', index=False)
        print("[SUCCESS] data/example_chatbot_dataset.csv created.")
    except Exception as e:
        print(f"Failed to create chatbot dataset example: {e}")

    # 2. Raw Instagram Dataset Example
    print("\nCreating example for raw instagram dataset...")
    try:
        raw_file = 'data/dataset_instagram-scraper_2026-05-05_12-08-22-179.csv'
        df_raw = pd.read_csv(raw_file, nrows=3)
        
        if 'caption' in df_raw.columns:
            df_raw['caption'] = [
                'Hayo siapa yang suka jajan sore? Cobain nih jajan di #warungcontoh #jajanansore',
                'Ngopi dulu yuk biar semangat! ☕ #kafesimulasi #ngopisore',
                'Steak time! 🥩 #restodummy #steakhouse'
            ]
            
        if 'ownerUsername' in df_raw.columns:
            df_raw['ownerUsername'] = ['jajan_sore_contoh', 'ngopi_dummy', 'steak_time_sim']
            
        if 'url' in df_raw.columns:
            df_raw['url'] = [
                'https://www.instagram.com/p/Example1/',
                'https://www.instagram.com/p/Example2/',
                'https://www.instagram.com/p/Example3/'
            ]
            
        if 'videoUrl' in df_raw.columns:
            df_raw['videoUrl'] = ['https://example.com/video1.mp4', 'https://example.com/video2.mp4', 'https://example.com/video3.mp4']
            
        df_raw.to_csv('data/example_raw_instagram.csv', index=False)
        print("[SUCCESS] data/example_raw_instagram.csv created.")
    except Exception as e:
        print(f"Failed to create raw instagram dataset example: {e}")

if __name__ == '__main__':
    create_examples()
