#!/usr/bin/env python3
"""
Instagram Video Downloader dengan Audio Extraction
Menggunakan yt-dlp untuk download dan ffmpeg untuk ekstraksi audio
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Cek apakah yt-dlp dan ffmpeg sudah terinstall"""
    dependencies = {
        'yt-dlp': 'yt-dlp --version',
        'ffmpeg': 'ffmpeg -version'
    }
    
    missing = []
    for name, command in dependencies.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"✓ {name} terinstall")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"✗ {name} tidak ditemukan")
            missing.append(name)
    
    return missing


def download_instagram_video(url, output_dir="downloads"):
    """Download video Instagram menggunakan yt-dlp"""
    # Buat folder output jika belum ada
    Path(output_dir).mkdir(exist_ok=True)
    
    # Template nama file
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
    
    print(f"\n📥 Mendownload video dari Instagram...")
    print(f"URL: {url}")
    
    # Command yt-dlp untuk download video terbaik
    command = [
        'yt-dlp',
        '-f', 'best',  # Format terbaik
        '-o', output_template,  # Output template
        '--no-playlist',  # Jangan download playlist
        url
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Video berhasil didownload")
        
        # Cari file yang baru didownload
        for line in result.stdout.split('\n'):
            if 'Destination:' in line or 'has already been downloaded' in line:
                # Extract filename dari output
                pass
        
        # Alternatif: cari file terbaru di folder downloads
        files = list(Path(output_dir).glob("*"))
        if files:
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            return str(latest_file)
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error saat download: {e}")
        print(e.stderr)
        return None


def extract_audio(video_path, audio_format="mp3"):
    """Ekstrak audio dari video menggunakan ffmpeg"""
    if not video_path or not os.path.exists(video_path):
        print("✗ File video tidak ditemukan")
        return None
    
    # Buat nama file audio
    video_file = Path(video_path)
    audio_file = video_file.with_suffix(f".{audio_format}")
    
    print(f"\n🎵 Mengekstrak audio dari video...")
    print(f"Input: {video_path}")
    print(f"Output: {audio_file}")
    
    # Command ffmpeg untuk ekstrak audio
    command = [
        'ffmpeg',
        '-i', video_path,  # Input file
        '-vn',  # No video
        '-acodec', 'libmp3lame' if audio_format == 'mp3' else 'copy',  # Audio codec
        '-q:a', '2',  # Quality (0-9, lower is better)
        '-y',  # Overwrite output file
        str(audio_file)
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"✓ Audio berhasil diekstrak: {audio_file}")
        return str(audio_file)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error saat ekstrak audio: {e}")
        return None


def download_audio_only(url, output_dir="downloads"):
    """Download dan langsung ekstrak audio (lebih efisien)"""
    Path(output_dir).mkdir(exist_ok=True)
    
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
    
    print(f"\n🎵 Mendownload dan mengekstrak audio...")
    print(f"URL: {url}")
    
    # Command yt-dlp untuk langsung download audio
    command = [
        'yt-dlp',
        '-x',  # Extract audio
        '--audio-format', 'mp3',  # Format audio
        '--audio-quality', '0',  # Quality terbaik
        '-o', output_template,
        '--no-playlist',
        url
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Audio berhasil didownload")
        
        # Cari file audio yang baru didownload
        audio_files = list(Path(output_dir).glob("*.mp3"))
        if audio_files:
            latest_file = max(audio_files, key=lambda x: x.stat().st_mtime)
            return str(latest_file)
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("Instagram Video Downloader & Audio Extractor")
    print("=" * 60)
    
    # Cek dependencies
    print("\n📋 Mengecek dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  Dependency yang hilang: {', '.join(missing)}")
        print("\nCara install:")
        if 'yt-dlp' in missing:
            print("  yt-dlp: pip install yt-dlp")
        if 'ffmpeg' in missing:
            print("  ffmpeg: Download dari https://ffmpeg.org/download.html")
            print("          atau gunakan package manager (choco install ffmpeg)")
        sys.exit(1)
    
    # Input URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("\n" + "=" * 60)
        url = input("Masukkan URL Instagram post: ").strip()
    
    if not url:
        print("✗ URL tidak boleh kosong")
        sys.exit(1)
    
    # Pilih mode
    print("\n" + "=" * 60)
    print("Pilih mode:")
    print("1. Download video + ekstrak audio (2 langkah)")
    print("2. Download audio saja (lebih cepat)")
    
    choice = input("\nPilihan (1/2) [default: 2]: ").strip() or "2"
    
    if choice == "1":
        # Mode 1: Download video dulu, lalu ekstrak
        video_file = download_instagram_video(url)
        if video_file:
            audio_file = extract_audio(video_file)
            if audio_file:
                print(f"\n✅ Selesai!")
                print(f"Video: {video_file}")
                print(f"Audio: {audio_file}")
    else:
        # Mode 2: Langsung download audio
        audio_file = download_audio_only(url)
        if audio_file:
            print(f"\n✅ Selesai!")
            print(f"Audio: {audio_file}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
