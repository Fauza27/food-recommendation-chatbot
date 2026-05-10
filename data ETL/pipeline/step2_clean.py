#!/usr/bin/env python3
"""
Transcription Data Cleaning and Formatting Pipeline.

Utilizes OpenAI's GPT models to correct spelling errors, typos, and 
contextual inaccuracies within the raw transcriptions. Incorporates 
available captions and user comments to enhance contextual accuracy.
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
    from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, check_openai_credentials
except ImportError:
    print("[WARNING] config.py not found, using environment variables directly")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
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

# Model settings (from config)
MODEL = OPENAI_MODEL
TEMPERATURE = OPENAI_TEMPERATURE
MAX_TOKENS = OPENAI_MAX_TOKENS

# File paths
INPUT_FILE = "data/chatbot_food_dataset.csv"
OUTPUT_FILE = "data/chatbot_food_dataset.csv"
PROGRESS_FILE = "cleaning_progress.json"

# Processing settings
BATCH_SIZE = 5  # Save setiap 5 baris
REQUEST_DELAY = 1  # Delay 1 detik antar request (rate limiting)
MAX_RETRIES = 3
RETRY_DELAY = 5

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
        "total_skipped": 0,
        "start_time": None
    }

def save_progress(progress):
    """Save progress ke file"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARNING] Tidak bisa save progress: {e}")

def create_cleaning_prompt(raw_transcribe, caption, comments):
    """Buat prompt untuk GPT"""
    
    # Build context
    context_parts = []
    if caption and str(caption).strip() and caption != 'nan':
        context_parts.append(f"Caption: {caption}")
    if comments and str(comments).strip() and comments != 'nan':
        context_parts.append(f"Komentar: {comments}")
    
    context = "\n".join(context_parts) if context_parts else "Tidak ada konteks tambahan."
    
    prompt = f"""Kamu adalah asisten yang ahli dalam membersihkan dan memperbaiki hasil transkripsi audio bahasa Indonesia.

Tugas: Perbaiki typo, kesalahan ejaan, dan kesalahan transkripsi pada teks berikut. Gunakan konteks dari caption dan komentar untuk membantu.

KONTEKS:
{context}

TRANSKRIPSI ASLI:
{raw_transcribe}

INSTRUKSI:
1. Perbaiki typo dan kesalahan ejaan
2. Perbaiki nama tempat, makanan, dan brand yang salah
3. Gunakan konteks dari caption/komentar untuk validasi
4. Pertahankan struktur kalimat dan makna asli
5. Jangan tambahkan informasi baru
6. Jika transkripsi dimulai dengan [ERROR] atau [NO AUDIO], kembalikan apa adanya
7. Output hanya teks yang sudah diperbaiki, tanpa penjelasan

TRANSKRIPSI YANG DIPERBAIKI:"""

    return prompt

def clean_with_gpt(raw_transcribe, caption, comments, retries=MAX_RETRIES):
    """Bersihkan transkripsi menggunakan GPT"""
    
    # Skip jika raw_transcribe kosong atau error/no audio
    if pd.isna(raw_transcribe) or not str(raw_transcribe).strip():
        return None, "Empty transcription"
    
    raw_str = str(raw_transcribe).strip()
    
    # Skip jika dimulai dengan marker error/no audio
    if raw_str.startswith('[ERROR') or raw_str.startswith('[NO AUDIO'):
        return raw_str, None  # Return as-is
    
    # Jika terlalu pendek (< 10 karakter), kembalikan apa adanya
    if len(raw_str) < 10:
        return raw_str, None
    
    # Buat prompt
    prompt = create_cleaning_prompt(raw_transcribe, caption, comments)
    
    # Retry loop
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Kamu adalah asisten pembersih transkripsi bahasa Indonesia yang akurat dan konsisten."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            cleaned = response.choices[0].message.content.strip()
            
            # Validasi output
            if cleaned and len(cleaned) > 0:
                return cleaned, None
            else:
                return raw_str, "Empty response from GPT"
                
        except openai.RateLimitError as e:
            if attempt < retries - 1:
                print(f"\n[WARNING]  Rate limit, waiting {RETRY_DELAY * (attempt + 1)}s...")
                time.sleep(RETRY_DELAY * (attempt + 1))
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

def estimate_cost(num_rows, avg_tokens_per_row=300):
    """Estimasi biaya OpenAI"""
    # GPT-4o-mini pricing (as of 2024)
    # Input: $0.150 / 1M tokens
    # Output: $0.600 / 1M tokens
    
    input_tokens = num_rows * avg_tokens_per_row
    output_tokens = num_rows * 200  # Estimasi output lebih pendek
    
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
    print("Executing Step 2: Clean Transcriptions with GPT")
    
    # Check for --yes flag
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    print(f"[OK] Loaded: {len(df)} rows")
    
    # Check if cleaned_transcribe column exists
    if 'cleaned_transcribe' not in df.columns:
        print("Creating 'cleaned_transcribe' column...")
        df['cleaned_transcribe'] = ''
    
    # Find rows that need cleaning
    has_raw = df['raw_transcribe'].notna() & (df['raw_transcribe'] != '')
    already_cleaned = df['cleaned_transcribe'].notna() & (df['cleaned_transcribe'] != '')
    needs_cleaning = has_raw & ~already_cleaned
    
    print(f"[STATS] Statistics:")
    print(f"   Total rows: {len(df)}")
    print(f"   Has raw_transcribe: {has_raw.sum()}")
    print(f"   Already cleaned: {already_cleaned.sum()}")
    print(f"   Needs cleaning: {needs_cleaning.sum()}")
    
    if needs_cleaning.sum() == 0:
        print("[OK] Semua baris sudah dibersihkan!")
        sys.exit(0)
    
    # Estimate cost
    cost_estimate = estimate_cost(needs_cleaning.sum())
    print(f"[BILLING] Estimasi Biaya OpenAI:")
    print(f"   Model: {MODEL}")
    print(f"   Rows to process: {needs_cleaning.sum()}")
    print(f"   Estimated tokens: {cost_estimate['input_tokens']:,} input + {cost_estimate['output_tokens']:,} output")
    print(f"   Estimated cost: ${cost_estimate['total_cost']:.4f}")
    print(f"   (Input: ${cost_estimate['input_cost']:.4f} + Output: ${cost_estimate['output_cost']:.4f})")
    
    # Confirm
    if not auto_confirm:
        confirm = input("Lanjutkan? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Dibatalkan.")
            sys.exit(0)
    else:
        print("Auto-confirmed (--yes flag)")
    
    print("MEMULAI PEMBERSIHAN")
    
    # Load progress
    progress = load_progress()
    if progress['start_time'] is None:
        progress['start_time'] = datetime.now().isoformat()
    
    # Process rows
    rows_to_process = df[needs_cleaning]
    
    success = 0
    errors = 0
    skipped = 0
    
    pbar = tqdm(total=len(rows_to_process), desc="Cleaning", unit="row")
    
    for idx, row in rows_to_process.iterrows():
        # Update progress bar
        pbar.set_postfix({
            "row": idx+1,
            "success": success,
            "errors": errors,
            "skipped": skipped
        })
        
        # Clean transcription
        cleaned, error_msg = clean_with_gpt(
            row['raw_transcribe'],
            row.get('caption', ''),
            row.get('user_comments', '')
        )
        
        progress['total_processed'] += 1
        progress['last_processed_index'] = idx
        
        if cleaned:
            # Success
            df.at[idx, 'cleaned_transcribe'] = cleaned
            success += 1
            progress['total_success'] += 1
        elif error_msg and error_msg in ["Empty transcription"]:
            # Skip
            df.at[idx, 'cleaned_transcribe'] = ''
            skipped += 1
            progress['total_skipped'] += 1
        else:
            # Error - keep raw
            df.at[idx, 'cleaned_transcribe'] = row['raw_transcribe']
            errors += 1
            progress['total_errors'] += 1
        
        pbar.update(1)
        
        # Save progress every BATCH_SIZE rows
        if (success + errors + skipped) % BATCH_SIZE == 0:
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
    
    # Update full_review with cleaned transcription
    print("Memperbarui kolom full_review...")
    df['full_review'] = (
        df['caption'].fillna('') + ' ' + 
        df['cleaned_transcribe'].fillna('') + ' ' + 
        df['user_comments'].fillna('')
    ).str.strip()
    df.to_csv(OUTPUT_FILE, index=False)
    print("[OK] full_review diperbarui dengan cleaned_transcribe")
    
    # Statistics
    print("STEP 2 COMPLETED")
    print(f"[STATS] Hasil:")
    print(f"   Diproses: {success + errors + skipped}")
    print(f"   Berhasil: {success} ({success/(success+errors+skipped)*100:.1f}%)")
    print(f"   Error: {errors} ({errors/(success+errors+skipped)*100:.1f}%)")
    print(f"   Dilewati: {skipped} ({skipped/(success+errors+skipped)*100:.1f}%)")
    print(f"[PATH] Output: {OUTPUT_FILE}")
    
    # Cleanup progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("[OK] Progress log dibersihkan")

if __name__ == "__main__":
    main()
