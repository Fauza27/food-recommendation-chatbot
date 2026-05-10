# Scripts

Helper scripts dan archived scripts.

## 📁 Structure

```
scripts/
├── instagram_downloader.py    # Helper: Download Instagram videos
└── archive/                   # Archived/old scripts
    ├── old/                   # Old transcription versions
    ├── improved/              # Improved transcription versions
    └── *.py                   # Other archived scripts
```

## 🔧 Helper Scripts

### instagram_downloader.py

Download video dari Instagram untuk ekstraksi audio.

**Usage**:
```python
from scripts.instagram_downloader import download_instagram_video

# Download video
video_path = download_instagram_video(instagram_url)
```

**Note**: Script ini digunakan untuk kasus khusus dimana audioUrl tidak tersedia.

## 📚 Main Pipeline

Untuk menjalankan pipeline utama, gunakan script di folder `pipeline/`:

```bash
python run_pipeline.py
```

Lihat `pipeline/README.md` untuk detail.

---

**Note**: Archive scripts disimpan untuk referensi, tapi tidak digunakan dalam pipeline aktif.
