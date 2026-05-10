# 02 - Pipeline Guide

Panduan lengkap menjalankan pipeline ETL untuk Food Chatbot Dataset.

## Overview

Pipeline ini mengubah data mentah Instagram menjadi dataset terstruktur untuk chatbot makanan melalui 4 tahapan:

```
Raw Instagram Data
 ↓
[1] Transkripsi Audio → raw_transcribe
 ↓
[2] Cleaning GPT → cleaned_transcribe
 ↓
[3] Ekstraksi Info → 11 kolom terstruktur
 ↓
[4] Link Lokasi → link_lokasi
 ↓
Final Dataset (34 kolom)
```

## Quick Start

### Menjalankan Semua Tahapan

```bash
python run_pipeline.py
```

### Menjalankan Tahapan Tertentu

```bash
# Hanya step 1
python run_pipeline.py --step 1

# Skip step 1 dan 2
python run_pipeline.py --skip 1,2
```

### Melihat Daftar Tahapan

```bash
python run_pipeline.py --list
```

## Tahapan Pipeline

### Step 1: Transkripsi Audio

**Script**: `scripts/batch_transcribe_csv.py`

**Fungsi**: Mengubah audio Instagram menjadi text menggunakan Azure Speech Service

**Input**:
- `data/dataset_instagram-scraper_*.csv` (kolom `audioUrl`)

**Output**:
- `data/transcribed_dataset_*.csv` (+ kolom `raw_transcribe`)

**Requirements**:
- Azure Speech Service API Key
- Azure Region

**Fitur**:
- Auto-save setiap 10 baris
- Resume capability (skip yang sudah ada)
- Retry mechanism (3x per audio)
- Handle empty audio URLs
- Progress tracking

**Estimasi**:
- Waktu: ~2-3 jam untuk 900 rows
- Biaya: GRATIS (Azure free tier: 5 jam/bulan)

**Command**:
```bash
python scripts/batch_transcribe_csv.py
```

---

### Step 2: Cleaning Transkripsi

**Script**: `clean_transcriptions_gpt.py`

**Fungsi**: Memperbaiki typo dan kesalahan transkripsi menggunakan GPT-4o-mini

**Input**:
- `data/transcribed_dataset_*.csv` (kolom `raw_transcribe`)

**Output**:
- `data/chatbot_food_dataset.csv` (+ kolom `cleaned_transcribe`)

**Requirements**:
- OpenAI API Key

**Fitur**:
- Auto-save setiap 5 baris
- Resume capability
- Retry mechanism (3x per row)
- Rate limiting (1s delay)
- Context-aware cleaning (gunakan caption + comments)
- Skip whitespace-only rows

**Estimasi**:
- Waktu: ~80 menit untuk 900 rows
- Biaya: ~$0.15 (Rp 2,400)

**Command**:
```bash
python clean_transcriptions_gpt.py
```

**Contoh Perbaikan**:
```
Raw: "bakso adjra kua nya enak banget"
Cleaned: "Bakso Az Zahra kuahnya enak banget"
```

---

### Step 3: Ekstraksi Informasi

**Script**: `extract_structured_info.py`

**Fungsi**: Mengekstrak informasi terstruktur dari text menggunakan GPT-4o-mini

**Input**:
- `data/chatbot_food_dataset.csv` (kolom `cleaned_transcribe`)

**Output**:
- `data/chatbot_food_dataset.csv` (+ 11 kolom baru)

**Kolom yang Diekstrak**:
1. `nama_tempat` - Nama restoran/warung
2. `lokasi` - Alamat lengkap
3. `kategori_makanan` - Jenis makanan (Indonesia, Chinese, dll)
4. `tipe_tempat` - Restoran, Warung, Kafe, dll
5. `range_harga` - Harga per porsi
6. `menu_andalan` - Menu signature
7. `fasilitas` - Parkir, WiFi, AC, dll
8. `jam_buka` - Format HH:MM
9. `jam_tutup` - Format HH:MM
10. `hari_operasional` - Senin-Minggu
11. `extracted_hashtags` - Hashtags dari caption

**Requirements**:
- OpenAI API Key

**Fitur**:
- Auto-save setiap 5 baris
- Resume capability
- Retry mechanism (3x per row)
- Rate limiting (1s delay)
- JSON validation
- Fallback values untuk data tidak lengkap

**Estimasi**:
- Waktu: ~90 menit untuk 900 rows
- Biaya: ~$0.20 (Rp 3,200)

**Command**:
```bash
python extract_structured_info.py
```

---

### Step 4: Menambahkan Link Lokasi

**Script**: `add_link_lokasi.py`

**Fungsi**: Matching dengan data Google Maps link dari `data_link.csv`

**Input**:
- `data/chatbot_food_dataset.csv`
- `data/data_link.csv` (kolom `url`, `link_lokasi`)

**Output**:
- `data/chatbot_food_dataset.csv` (+ kolom `link_lokasi`)

**Matching Method**:
- Match by Instagram URL (`url` column)

**Fitur**:
- Exact URL matching
- Handle missing links
- Validation Google Maps URL

**Hasil**:
- 706/900 rows matched (78.4%)
- 380 rows dengan Google Maps link valid
- 249 rows "Link tidak tersedia"
- 77 rows "Tidak Ditemukan"
- 194 rows tidak ada match

**Command**:
```bash
python add_link_lokasi.py
```

---

## Estimasi Total Biaya

| Tahapan | Service | Biaya |
|---------|---------|-------|
| Step 1: Transkripsi | Azure Speech | **GRATIS** (free tier) |
| Step 2: Cleaning | OpenAI GPT-4o-mini | ~$0.15 |
| Step 3: Ekstraksi | OpenAI GPT-4o-mini | ~$0.20 |
| Step 4: Link Lokasi | - | GRATIS |
| **TOTAL** | | **~$0.35** (~Rp 5,600) |

**Untuk 900 rows data**

## ⏱️ Estimasi Total Waktu

| Tahapan | Waktu |
|---------|-------|
| Step 1: Transkripsi | ~2-3 jam |
| Step 2: Cleaning | ~80 menit |
| Step 3: Ekstraksi | ~90 menit |
| Step 4: Link Lokasi | ~1 menit |
| **TOTAL** | **~5-6 jam** |

## Setup Environment Variables

### Azure Speech Service

```bash
# Windows CMD
set AZURE_SPEECH_KEY=your-key-here
set AZURE_REGION=southeastasia

# Windows PowerShell
$env:AZURE_SPEECH_KEY="your-key-here"
$env:AZURE_REGION="southeastasia"

# Linux/macOS
export AZURE_SPEECH_KEY=your-key-here
export AZURE_REGION=southeastasia
```

### OpenAI API

```bash
# Windows CMD
set OPENAI_API_KEY=sk-proj-your-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-your-key-here"

# Linux/macOS
export OPENAI_API_KEY=sk-proj-your-key-here
```

## Output Dataset

**File**: `data/chatbot_food_dataset.csv`

**Struktur**: 900 rows × 34 columns

**Kolom Utama**:
- `full_review` - Review lengkap (gabungan semua info)
- `cleaned_transcribe` - Transkripsi yang sudah dibersihkan
- `nama_tempat` - Nama restoran
- `lokasi` - Alamat
- `kategori_makanan` - Jenis makanan
- `range_harga` - Harga
- `menu_andalan` - Menu signature
- `link_lokasi` - Google Maps link

Lihat detail lengkap di `04_DATASET_INFO.md`

## Resume & Recovery

Semua script mendukung **resume capability**:

- Auto-save progress secara berkala
- Skip rows yang sudah diproses
- Dapat di-interrupt dan dilanjutkan kapan saja

**Cara Resume**:
```bash
# Jalankan script yang sama lagi
python clean_transcriptions_gpt.py

# Script otomatis skip rows yang sudah ada
```

## Best Practices

### 1. Jalankan Step by Step

Untuk kontrol lebih baik, jalankan satu step dulu:

```bash
python run_pipeline.py --step 1
# Cek hasil
python run_pipeline.py --step 2
# Cek hasil
# dst...
```

### 2. Backup Data

Backup sebelum menjalankan pipeline:

```bash
# Windows
copy data\chatbot_food_dataset.csv data\chatbot_food_dataset_backup.csv

# Linux/macOS
cp data/chatbot_food_dataset.csv data/chatbot_food_dataset_backup.csv
```

### 3. Monitor Progress

Semua script menampilkan progress bar dan estimasi waktu:

```
Processing: 100%|████████████| 900/900 [1:20:00<00:00, 5.33s/row]
```

### 4. Check Logs

Jika ada error, cek output console untuk detail error message.

## Troubleshooting

Lihat `05_TROUBLESHOOTING.md` untuk solusi masalah umum.

## Referensi

- Setup Azure: `03_SETUP_GUIDE.md`
- Setup OpenAI: `03_SETUP_GUIDE.md`
- Dataset Info: `04_DATASET_INFO.md`
- Troubleshooting: `05_TROUBLESHOOTING.md`

---

**Happy Processing! **
