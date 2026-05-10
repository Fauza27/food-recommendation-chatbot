#!/usr/bin/env python3
"""
Information Extraction Pipeline.

Extracts structured JSON metadata (e.g., location, categories, pricing, menus)
from cleaned transcriptions, captions, and hashtags using OpenAI's GPT models.
The extracted attributes are used to enrich the chatbot's knowledge base.
"""

import os
import sys
import pandas as pd
import openai
import time
import json
from tqdm import tqdm
from datetime import datetime

# Load configuration from .env file
try:
    from config import OPENAI_API_KEY, OPENAI_MODEL, check_openai_credentials
except ImportError:
    print("[WARNING] config.py not found, using environment variables directly")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def check_openai_credentials():
        if not OPENAI_API_KEY:
            print("[ERROR] OPENAI_API_KEY tidak ditemukan!")
            print("Silakan set environment variable atau buat file .env")
            return False
        return True

# Check credentials
if not check_openai_credentials():
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Model settings
MODEL = OPENAI_MODEL
TEMPERATURE = 0.2  # Low temperature untuk konsistensi
MAX_TOKENS = 800

# File paths
INPUT_FILE = "data/chatbot_food_dataset.csv"
OUTPUT_FILE = "data/chatbot_food_dataset.csv"
PROGRESS_FILE = "extraction_progress.json"

# Processing settings
BATCH_SIZE = 5  # Save setiap 5 baris
REQUEST_DELAY = 1  # Delay 1 detik antar request
MAX_RETRIES = 3
RETRY_DELAY = 5

# Kolom baru yang akan dibuat
NEW_COLUMNS = [
    'nama_tempat',
    'lokasi',
    'kategori_makanan',
    'tipe_tempat',
    'range_harga',
    'menu_andalan',
    'fasilitas',
    'jam_buka',
    'jam_tutup',
    'hari_operasional',
    'extracted_hashtags'
]

def load_progress():
    """Load progress dari file"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "last_processed_index": -1,
        "total_processed": 0,
        "total_success": 0,
        "total_errors": 0,
        "start_time": None
    }

def save_progress(progress):
    """Save progress ke file"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARNING] Tidak bisa save progress: {e}")

def create_extraction_prompt(cleaned_transcribe, caption, hashtags, locationName):
    """Buat prompt untuk ekstraksi informasi"""
    
    # Build text content
    text_parts = []
    if caption and str(caption).strip() and caption != 'nan':
        text_parts.append(f"CAPTION:\n{caption}")
    if cleaned_transcribe and str(cleaned_transcribe).strip() and cleaned_transcribe != 'nan':
        text_parts.append(f"TRANSKRIPSI:\n{cleaned_transcribe}")
    if hashtags and str(hashtags).strip() and hashtags != 'nan':
        text_parts.append(f"HASHTAGS:\n{hashtags}")
    if locationName and str(locationName).strip() and locationName != 'nan':
        text_parts.append(f"LOCATION NAME:\n{locationName}")
    
    content = "\n\n".join(text_parts) if text_parts else "Tidak ada konten."
    
    prompt = f"""Kamu adalah asisten ekstraksi informasi kuliner dari konten Instagram food blogger.

KONTEN:
{content}

TUGAS:
Ekstrak informasi berikut dalam format JSON. Jika informasi tidak tersedia, gunakan null.

FORMAT OUTPUT (JSON):
{{
  "nama_tempat": "Nama restoran/warung/tempat makan",
  "lokasi": "Alamat lengkap atau area (contoh: Jl. Siradj Salman, Samarinda atau Blok M Jakarta Selatan)",
  "kategori_makanan": "Kategori makanan (contoh: Bakso, Mie Goreng, Nasi Goreng, Sate, Seafood, dll)",
  "tipe_tempat": "Tipe tempat (contoh: Warung, Restoran, Kafe, Food Court, Street Food, dll)",
  "range_harga": "Range harga dalam format 'X - Y K' atau 'X K' (contoh: 15 - 25 K, 50 K, dll)",
  "menu_andalan": "Menu andalan/signature dish yang disebutkan (pisahkan dengan koma jika lebih dari 1)",
  "fasilitas": "Fasilitas yang disebutkan (contoh: Parkir, AC, Wifi, Outdoor Seating, dll - pisahkan dengan koma)",
  "jam_buka": "Jam buka (format HH:MM, contoh: 08:00, 12:00)",
  "jam_tutup": "Jam tutup (format HH:MM atau 'habis' jika sampai habis)",
  "hari_operasional": "Hari operasional (contoh: Senin-Minggu, Senin-Jumat, Weekday, Weekend, dll)",
  "extracted_hashtags": "Hashtags yang relevan dengan makanan/tempat (pisahkan dengan koma, tanpa #)"
}}

ATURAN:
1. Ekstrak HANYA informasi yang JELAS disebutkan dalam konten
2. Jangan menebak atau menambahkan informasi yang tidak ada
3. Untuk nama_tempat, prioritaskan nama yang disebutkan di caption atau mention (@)
4. Untuk lokasi, gabungkan informasi jalan, area, dan kota jika tersedia
5. Untuk kategori_makanan, fokus pada jenis makanan utama yang dibahas
6. Untuk range_harga, ekstrak angka yang disebutkan (contoh: "15 ribu sampai 25 ribu" → "15 - 25 K")
7. Untuk jam operasional, perhatikan kata kunci seperti "buka jam", "tutup jam", "sampai habis"
8. Untuk hashtags, ambil yang relevan dengan makanan/lokasi (abaikan hashtag umum seperti #viral)
9. Output HANYA JSON, tanpa penjelasan tambahan
10. Pastikan JSON valid dan bisa di-parse

CONTOH OUTPUT:
{{
  "nama_tempat": "Bakso Bobo Boho",
  "lokasi": "Jl. Siradj Salman, Samarinda",
  "kategori_makanan": "Bakso",
  "tipe_tempat": "Warung",
  "range_harga": "15 - 25 K",
  "menu_andalan": "Bakso Jamur, Bakso Telur, Bakso Campur",
  "fasilitas": null,
  "jam_buka": null,
  "jam_tutup": null,
  "hari_operasional": null,
  "extracted_hashtags": "baksosamarinda, kulinersamarinda, makanansamarinda"
}}

OUTPUT JSON:"""

    return prompt

def extract_with_gpt(cleaned_transcribe, caption, hashtags, locationName, retries=MAX_RETRIES):
    """Ekstrak informasi menggunakan GPT"""
    
    # Skip jika tidak ada konten
    has_content = False
    for field in [cleaned_transcribe, caption]:
        if field and str(field).strip() and str(field) != 'nan':
            has_content = True
            break
    
    if not has_content:
        return None, "No content to extract"
    
    # Buat prompt
    prompt = create_extraction_prompt(cleaned_transcribe, caption, hashtags, locationName)
    
    # Retry loop
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Kamu adalah asisten ekstraksi informasi kuliner yang akurat. Output hanya JSON valid tanpa penjelasan."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            try:
                result = json.loads(result_text)
                
                # Validate required keys
                for key in NEW_COLUMNS:
                    if key not in result:
                        result[key] = None
                
                return result, None
                
            except json.JSONDecodeError as e:
                if attempt < retries - 1:
                    continue
                else:
                    return None, f"Invalid JSON: {str(e)}"
                
        except openai.RateLimitError as e:
            if attempt < retries - 1:
                wait_time = RETRY_DELAY * (attempt + 1)
                print(f"\n[WARNING]  Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                return None, f"Rate limit exceeded: {str(e)}"
                
        except openai.APIError as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None, f"API error: {str(e)}"
                
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None, f"Error: {str(e)}"
    
    return None, "Max retries exceeded"

def estimate_cost(num_rows, avg_tokens_per_row=600):
    """Estimasi biaya OpenAI"""
    # GPT-4o-mini pricing
    # Input: $0.150 / 1M tokens
    # Output: $0.600 / 1M tokens
    
    input_tokens = num_rows * avg_tokens_per_row
    output_tokens = num_rows * 300  # JSON output
    
    input_cost = (input_tokens / 1_000_000) * 0.150
    output_cost = (output_tokens / 1_000_000) * 0.600
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost
    }

def main():
    print("Executing Step 3: Extract Structured Information")
    
    # Check for --yes flag
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    print(f"[OK] Loaded: {len(df)} rows")
    
    # Create new columns if not exist
    for col in NEW_COLUMNS:
        if col not in df.columns:
            df[col] = None
    
    # Find rows that need extraction
    has_content = (
        (df['cleaned_transcribe'].notna() & (df['cleaned_transcribe'] != '')) |
        (df['caption'].notna() & (df['caption'] != ''))
    )
    already_extracted = df['nama_tempat'].notna() & (df['nama_tempat'] != '')
    needs_extraction = has_content & ~already_extracted
    
    print(f"[STATS] Statistics:")
    print(f"   Total rows: {len(df)}")
    print(f"   Has content: {has_content.sum()}")
    print(f"   Already extracted: {already_extracted.sum()}")
    print(f"   Needs extraction: {needs_extraction.sum()}")
    
    if needs_extraction.sum() == 0:
        print("[OK] Semua baris sudah diekstrak!")
        sys.exit(0)
    
    # Estimate cost
    cost_estimate = estimate_cost(needs_extraction.sum())
    print(f"[BILLING] Estimasi Biaya OpenAI:")
    print(f"   Model: {MODEL}")
    print(f"   Rows to process: {needs_extraction.sum()}")
    print(f"   Estimated tokens: {cost_estimate['input_tokens']:,} input + {cost_estimate['output_tokens']:,} output")
    print(f"   Estimated cost: ${cost_estimate['total_cost']:.4f} (Rp {cost_estimate['total_cost']*16000:.0f})")
    print(f"   (Input: ${cost_estimate['input_cost']:.4f} + Output: ${cost_estimate['output_cost']:.4f})")
    
    print(f"📋 Kolom yang akan dibuat:")
    for i, col in enumerate(NEW_COLUMNS, 1):
        print(f"   {i:2d}. {col}")
    
    # Confirm
    if not auto_confirm:
        confirm = input("Lanjutkan? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Dibatalkan.")
            sys.exit(0)
    else:
        print("Auto-confirmed (--yes flag)")
    
    print("MEMULAI EKSTRAKSI")
    
    # Load progress
    progress = load_progress()
    if progress['start_time'] is None:
        progress['start_time'] = datetime.now().isoformat()
    
    # Process rows
    rows_to_process = df[needs_extraction]
    
    success = 0
    errors = 0
    
    pbar = tqdm(total=len(rows_to_process), desc="Extracting", unit="row")
    
    for idx, row in rows_to_process.iterrows():
        # Update progress bar
        pbar.set_postfix({
            "row": idx+1,
            "success": success,
            "errors": errors
        })
        
        # Extract information
        result, error_msg = extract_with_gpt(
            row.get('cleaned_transcribe', ''),
            row.get('caption', ''),
            row.get('hashtags', ''),
            row.get('locationName', '')
        )
        
        progress['total_processed'] += 1
        progress['last_processed_index'] = idx
        
        if result:
            # Success - update all columns
            for col in NEW_COLUMNS:
                df.at[idx, col] = result.get(col)
            success += 1
            progress['total_success'] += 1
        else:
            # Error - leave empty
            errors += 1
            progress['total_errors'] += 1
        
        pbar.update(1)
        
        # Save progress every BATCH_SIZE rows
        if (success + errors) % BATCH_SIZE == 0:
            df.to_csv(OUTPUT_FILE, index=False)
            save_progress(progress)
        
        # Rate limiting delay
        time.sleep(REQUEST_DELAY)
    
    pbar.close()
    
    # Final save
    print("Menyimpan hasil akhir...")
    df.to_csv(OUTPUT_FILE, index=False)
    save_progress(progress)
    print("[OK] Tersimpan")
    
    # Statistics
    print("STEP 3 COMPLETED")
    print(f"[STATS] Hasil:")
    print(f"   Diproses: {success + errors}")
    print(f"   Berhasil: {success} ({success/(success+errors)*100:.1f}%)")
    print(f"   Error: {errors} ({errors/(success+errors)*100:.1f}%)")
    
    # Show sample results
    print("📋 Sample hasil ekstraksi (5 baris pertama):")
    sample_cols = ['nama_tempat', 'lokasi', 'kategori_makanan', 'range_harga', 'menu_andalan']
    sample_df = df[df['nama_tempat'].notna()][sample_cols].head()
    for idx, row in sample_df.iterrows():
        print(f"Row {idx+1}:")
        for col in sample_cols:
            val = row[col]
            if val and str(val) != 'nan':
                print(f"  {col}: {val}")
    
    print(f"[PATH] Output: {OUTPUT_FILE}")
    
    # Cleanup progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("[OK] Progress log dibersihkan")

if __name__ == "__main__":
    main()
