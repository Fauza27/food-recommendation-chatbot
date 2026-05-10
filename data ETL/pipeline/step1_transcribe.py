#!/usr/bin/env python3
"""
Azure Speech Service Continuous Recognition Transcription Pipeline.

Extracts audio from video URLs, converts to WAV format via FFmpeg,
and transcribes Indonesian speech using Azure Cognitive Services.
Implements continuous recognition to avoid context loss on long audios.

Key Mechanisms:
- Stateful Execution: Auto-saves progress incrementally to allow resuming.
- Fault Tolerance: Retry mechanisms for HTTP and API failures.
- Rate Limit Compliance: Controlled request delays.
- Telemetry: Usage tracking against Azure Free Tier limits (300 mins/month).
"""

import os
import sys
import pandas as pd
import requests
from pathlib import Path
import subprocess
import azure.cognitiveservices.speech as speechsdk
import time
from datetime import datetime
from tqdm import tqdm
import json
import shutil

# Load configuration from .env file
try:
    from config import AZURE_SPEECH_KEY, AZURE_REGION, check_azure_credentials
except ImportError:
    print("[WARNING] config.py not found, using environment variables directly")
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
    AZURE_REGION = os.getenv("AZURE_REGION", "southeastasia")
    
    def check_azure_credentials():
        if not AZURE_SPEECH_KEY:
            print("[ERROR] AZURE_SPEECH_KEY tidak ditemukan!")
            print("Silakan set environment variable atau buat file .env")
            return False
        return True

INPUT_CSV = "dataset_instagram-scraper_2026-05-05_12-08-22-179.csv"

OUTPUT_CSV = f"transcribed_{INPUT_CSV}"

LANGUAGE_CODE = "id-ID"

TEMP_AUDIO_DIR = "temp_audio"

MAX_RETRIES = 3
RETRY_DELAY = 5  # detik

REQUEST_DELAY = 2  # detik

SAVE_EVERY_N_ROWS = 1  # Save setiap row (untuk safety maksimal)
BACKUP_EVERY_N_ROWS = 10  # Backup setiap 10 rows

MEMORY_EFFICIENT_MODE = True  # Set False jika ingin save semua kolom (butuh RAM besar!)

PROGRESS_LOG = "batch_progress.json"

def check_credentials():
    """Cek apakah credentials sudah di-set"""
    return check_azure_credentials()

def load_progress():
    """Load progress dari file log"""
    if os.path.exists(PROGRESS_LOG):
        try:
            with open(PROGRESS_LOG, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "last_processed_index": -1,
        "total_processed": 0,
        "total_success": 0,
        "total_errors": 0,
        "total_duration_seconds": 0,
        "start_time": None,
        "last_update": None
    }

def save_progress(progress):
    """Save progress ke file log"""
    progress["last_update"] = datetime.now().isoformat()
    try:
        with open(PROGRESS_LOG, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        print(f"[WARNING] Could not save progress: {e}")

def create_backup(csv_file):
    """Buat backup file CSV"""
    if os.path.exists(csv_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{csv_file}.backup_{timestamp}"
        try:
            shutil.copy2(csv_file, backup_file)
            return backup_file
        except Exception as e:
            print(f"[WARNING] Could not create backup: {e}")
    return None

def download_audio(url, output_dir=TEMP_AUDIO_DIR):
    """Download audio dari URL dengan retry"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate filename dari URL
    filename = f"audio_{hash(url) % 10000000}.mp4"
    filepath = os.path.join(output_dir, filename)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return filepath
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return None
    
    return None

def convert_to_wav(input_file):
    """Konversi ke WAV untuk Azure"""
    output_file = str(Path(input_file).with_suffix('.wav'))
    
    try:
        command = [
            'ffmpeg', '-i', str(input_file),  # Ensure string
            '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            '-y', str(output_file)  # Ensure string
        ]
        
        result = subprocess.run(command, capture_output=True)
        
        # Check if output file exists and has content
        if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
            # Hapus file asli
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
            except:
                pass
            return output_file
        else:
            # Debug: print error if conversion failed
            # print(f"DEBUG: Conversion failed for {input_file}")
            # print(f"DEBUG: Return code: {result.returncode}")
            return None
            
    except Exception as e:
        # print(f"DEBUG: Exception in convert_to_wav: {e}")
        return None

def get_audio_duration(audio_file):
    """Get audio duration in seconds"""
    try:
        command = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_file
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def transcribe_audio_azure(audio_file, language=LANGUAGE_CODE):
    """
    Transkripsi audio menggunakan Azure Continuous Recognition
    No chunking = No context loss!
    """
    try:
        # Setup speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_REGION
        )
        speech_config.speech_recognition_language = language
        
        # Enable fitur untuk kualitas terbaik
        speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
        speech_config.request_word_level_timestamps()
        speech_config.enable_dictation()
        
        # Setup audio config
        audio_config = speechsdk.AudioConfig(filename=audio_file)
        
        # Create continuous recognition
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Collect all results
        all_results = []
        done = False
        error_message = None
        
        def recognized_cb(evt):
            """Callback untuk setiap segment yang dikenali"""
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                all_results.append(evt.result.text)
        
        def canceled_cb(evt):
            """Callback untuk error"""
            nonlocal done, error_message
            if evt.reason == speechsdk.CancellationReason.Error:
                error_message = f"Error: {evt.error_details}"
            done = True
        
        def stop_cb(evt):
            """Callback ketika selesai"""
            nonlocal done
            done = True
        
        # Connect callbacks
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(canceled_cb)
        
        # Start continuous recognition
        speech_recognizer.start_continuous_recognition()
        
        # Wait until done (with timeout)
        timeout = 300  # 5 minutes max
        start_time = time.time()
        while not done and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        # Stop recognition
        speech_recognizer.stop_continuous_recognition()
        
        # Check for errors
        if error_message:
            return None, error_message
        
        # Combine all results
        full_transcript = " ".join(all_results)
        
        return full_transcript if full_transcript else None, None
            
    except Exception as e:
        return None, str(e)

def transcribe_url(audio_url, language=LANGUAGE_CODE):
    """
    Main function: Download, convert, transcribe, cleanup
    Returns: (transcript, duration_seconds, error_message)
    """
    if pd.isna(audio_url) or not audio_url or audio_url.strip() == "":
        return "", 0, None
    
    audio_file = None
    wav_file = None
    
    try:
        # Download
        audio_file = download_audio(audio_url)
        if not audio_file:
            return None, 0, "Download failed"
        
        # Convert to WAV
        wav_file = convert_to_wav(audio_file)
        if not wav_file:
            return None, 0, "Conversion failed"
        
        # Get duration
        duration = get_audio_duration(wav_file)
        
        # Transcribe with retry
        transcript = None
        error_msg = None
        
        for attempt in range(MAX_RETRIES):
            transcript, error_msg = transcribe_audio_azure(wav_file, language)
            
            if transcript:
                break
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        
        # Cleanup
        if wav_file and os.path.exists(wav_file):
            try:
                os.remove(wav_file)
            except:
                pass
        
        if transcript:
            return transcript, duration, None
        else:
            return None, duration, error_msg or "Transcription failed"
        
    except Exception as e:
        # Cleanup on error
        for f in [audio_file, wav_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        
        return None, 0, str(e)

def cleanup_temp_dirs():
    """Hapus folder temporary"""
    if os.path.exists(TEMP_AUDIO_DIR):
        try:
            shutil.rmtree(TEMP_AUDIO_DIR)
        except:
            pass

def format_duration(seconds):
    """Format duration ke human readable"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def main():
    print("Executing Step 1: Azure Audio Transcription")
    
    # Check credentials
    if not check_credentials():
        sys.exit(1)
    
    # Resolve file paths
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir = Path(".")
    
    input_path = data_dir / INPUT_CSV
    output_path = data_dir / OUTPUT_CSV
    
    # Check input file
    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)
    
    print(f"[PATH] Input CSV: {input_path}")
    print(f"[PATH] Output CSV: {output_path}")
    print(f"[PATH] Progress Log: {PROGRESS_LOG}")
    
    # Load progress
    progress = load_progress()
    
    if progress["last_processed_index"] >= 0:
        print(f"[STATS] Resuming from previous session:")
        print(f"   Last processed: Row {progress['last_processed_index']}")
        print(f"   Total processed: {progress['total_processed']}")
        print(f"   Success: {progress['total_success']}")
        print(f"   Errors: {progress['total_errors']}")
        print(f"   Total duration: {format_duration(progress['total_duration_seconds'])}")
    
    # Load CSV
    print("Loading CSV...")
    try:
        # Try to load output file first (for resume)
        if output_path.exists():
            if MEMORY_EFFICIENT_MODE:
                # Load only essential columns to save memory
                df = pd.read_csv(output_path, usecols=['audioUrl', 'raw_transcribe'], dtype={'audioUrl': str, 'raw_transcribe': str})
                print(f"[OK] Loaded existing output file (resume mode)")
                print(f"[OK] Memory-efficient mode: {len(df.columns)} columns")
            else:
                df = pd.read_csv(output_path, low_memory=False)
                print(f"[OK] Loaded existing output file (resume mode)")
                print(f"[OK] Full mode: {len(df.columns)} columns")
        else:
            if MEMORY_EFFICIENT_MODE:
                # Load only essential columns from input
                # First, check what columns exist
                df_sample = pd.read_csv(input_path, nrows=1)
                
                # Select only columns we need
                cols_to_load = ['audioUrl']
                if 'caption' in df_sample.columns:
                    cols_to_load.append('caption')
                
                df = pd.read_csv(input_path, usecols=cols_to_load, dtype=str)
                print(f"[OK] Loaded input file (new session)")
                print(f"[OK] Memory-efficient mode: {len(df.columns)} columns")
            else:
                df = pd.read_csv(input_path, low_memory=False)
                print(f"[OK] Loaded input file (new session)")
                print(f"[OK] Full mode: {len(df.columns)} columns")
        
        print(f"[OK] Total rows: {len(df)}")
    except Exception as e:
        print(f"[ERROR] Error loading CSV: {e}")
        sys.exit(1)
    
    # Check if audioUrl column exists
    if 'audioUrl' not in df.columns:
        print(f"[ERROR] Column 'audioUrl' not found in CSV")
        print(f"   Available columns: {', '.join(df.columns[:10])}...")
        sys.exit(1)
    
    print(f"[OK] Found 'audioUrl' column")
    
    # Add raw_transcribe column if not exists
    if 'raw_transcribe' not in df.columns:
        df['raw_transcribe'] = ""
    
    # Count rows to process
    non_empty = df['audioUrl'].notna() & (df['audioUrl'] != '')
    
    # Check for already done transcriptions (handle NaN values properly)
    if 'raw_transcribe' in df.columns:
        # Fill NaN with empty string first to avoid type errors
        df['raw_transcribe'] = df['raw_transcribe'].fillna('')
        already_done = (df['raw_transcribe'] != '') & (~df['raw_transcribe'].str.startswith('[ERROR'))
    else:
        already_done = pd.Series([False] * len(df), index=df.index)
    
    total_rows = len(df)
    rows_with_audio = non_empty.sum()
    rows_already_done = already_done.sum()
    rows_to_process = (non_empty & ~already_done).sum()
    
    print("[INFO] Target summary:")
    print(f"  Total: {total_rows}")
    print(f"  Valid audioUrl: {rows_with_audio}")
    print(f"  Already done: {rows_already_done}")
    print(f"  Remaining: {rows_to_process}")
    
    if rows_to_process == 0:
        print("[OK] All rows already transcribed!")
        print(f"   Output file: {output_path}")
        sys.exit(0)
    
    # Estimate duration & cost
    avg_duration = 60  # Assume 60 seconds average
    estimated_minutes = (rows_to_process * avg_duration) / 60
    free_tier_minutes = 300  # Azure free tier
    
    print(f"[BILLING] Azure Free Tier Tracking:")
    print(f"   Current usage: {format_duration(progress['total_duration_seconds'])}")
    print(f"   Estimated new: {estimated_minutes:.1f} minutes")
    print(f"   Free tier limit: {free_tier_minutes} minutes/month")
    
    if progress['total_duration_seconds'] / 60 + estimated_minutes > free_tier_minutes:
        print(f"   [WARNING]  WARNING: May exceed free tier!")
    else:
        remaining = free_tier_minutes - (progress['total_duration_seconds'] / 60 + estimated_minutes)
        print(f"   [OK] Within free tier (remaining: {remaining:.1f} min)")
    
    # Confirm
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    print("STARTING TRANSCRIPTION")
    
    # Initialize progress if new session
    if progress["start_time"] is None:
        progress["start_time"] = datetime.now().isoformat()
    
    # Process each row
    start_time = time.time()
    processed_this_session = 0
    success_this_session = 0
    errors_this_session = 0
    
    # Create progress bar
    pbar = tqdm(total=rows_to_process, desc="Transcribing", unit="audio")
    
    for idx, row in df.iterrows():
        # Skip if no audioUrl
        if pd.isna(row['audioUrl']) or row['audioUrl'].strip() == "":
            continue
        
        # Skip if already transcribed (and not error)
        existing = row.get('raw_transcribe', '')
        if pd.notna(existing) and existing.strip() != "" and not existing.startswith('[ERROR'):
            continue
        
        # Update progress bar
        pbar.set_postfix({
            "row": idx+1,
            "success": success_this_session,
            "errors": errors_this_session
        })
        
        # Transcribe
        transcript, duration, error_msg = transcribe_url(row['audioUrl'], LANGUAGE_CODE)
        
        processed_this_session += 1
        progress["total_processed"] += 1
        progress["last_processed_index"] = idx
        
        if transcript:
            # Success
            df.at[idx, 'raw_transcribe'] = transcript
            success_this_session += 1
            progress["total_success"] += 1
            progress["total_duration_seconds"] += duration
        else:
            # Error
            error_text = f"[ERROR: {error_msg}]" if error_msg else "[ERROR: Unknown]"
            df.at[idx, 'raw_transcribe'] = error_text
            errors_this_session += 1
            progress["total_errors"] += 1
        
        pbar.update(1)
        
        # Auto-save every N rows
        if processed_this_session % SAVE_EVERY_N_ROWS == 0:
            try:
                # Save with minimal memory footprint
                df.to_csv(output_path, index=False)
                save_progress(progress)
            except Exception as e:
                print(f"\n[WARNING] Could not save progress: {e}")
                # Last resort: save progress log only
                save_progress(progress)
        
        # Backup every N rows
        if processed_this_session % BACKUP_EVERY_N_ROWS == 0:
            create_backup(str(output_path))
        
        # Delay to avoid rate limit
        time.sleep(REQUEST_DELAY)
    
    pbar.close()
    
    # Final save
    print("SAVING FINAL RESULTS")
    
    try:
        # Save with minimal memory footprint
        df.to_csv(output_path, index=False)
        save_progress(progress)
        
        # Create final backup
        backup_file = create_backup(str(output_path))
        if backup_file:
            print(f"[OK] Backup created: {backup_file}")
        
        print(f"[OK] Saved to: {output_path}")
        
        # Show what columns were saved
        cols_saved = list(df.columns)
        print(f"   (Contains: {', '.join(cols_saved)})")
    except Exception as e:
        print(f"[WARNING]  Error saving CSV: {e}")
        print("   Progress is saved in batch_progress.json")
        print("   You can resume later")
    
    # Cleanup
    cleanup_temp_dirs()
    
    # Statistics
    elapsed = time.time() - start_time
    total_duration_minutes = progress["total_duration_seconds"] / 60
    
    print("COMPLETED")
    print("[STATS] This Session:")
    print(f"   Processed: {processed_this_session}")
    print(f"   Successful: {success_this_session}")
    print(f"   Errors: {errors_this_session}")
    print(f"   Time elapsed: {elapsed/60:.1f} minutes")
    print("[STATS] Total (All Sessions):")
    print(f"   Processed: {progress['total_processed']}")
    print(f"   Successful: {progress['total_success']}")
    print(f"   Errors: {progress['total_errors']}")
    print(f"   Audio duration: {format_duration(progress['total_duration_seconds'])}")
    print("[BILLING] Azure Free Tier Usage:")
    print(f"   Used: {total_duration_minutes:.1f} / 300 minutes")
    print(f"   Remaining: {300 - total_duration_minutes:.1f} minutes")
    
    if total_duration_minutes > 300:
        print(f"   [WARNING]  Exceeded free tier by {total_duration_minutes - 300:.1f} minutes")
    
    print(f"[PATH] Output file: {output_path}")
    print(f"[PATH] Progress log: {PROGRESS_LOG}")
    
    # Cleanup progress log if all done
    if rows_to_process == processed_this_session:
        try:
            os.remove(PROGRESS_LOG)
            print("[OK] All done! Progress log cleaned up.")
        except:
            pass

if __name__ == "__main__":
    main()
