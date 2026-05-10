# Pipeline Scripts

Script-script utama untuk ETL pipeline Food Chatbot Dataset.

## 📋 Pipeline Steps

### Step 1: Transkripsi Audio
**File**: `step1_transcribe.py`

Mengubah audio Instagram menjadi text menggunakan Azure Speech Service.

**Requirements**:
- `AZURE_SPEECH_KEY` environment variable
- `AZURE_REGION` environment variable

**Input**: `data/dataset_instagram-scraper_*.csv`
**Output**: `data/transcribed_dataset_*.csv` (+ kolom `raw_transcribe`)

**Run**:
```bash
python pipeline/step1_transcribe.py
```

---

### Step 2: Cleaning Transkripsi
**File**: `step2_clean.py`

Memperbaiki typo dan kesalahan transkripsi menggunakan GPT-4o-mini.

**Requirements**:
- `OPENAI_API_KEY` environment variable

**Input**: `data/transcribed_dataset_*.csv`
**Output**: `data/chatbot_food_dataset.csv` (+ kolom `cleaned_transcribe`)

**Run**:
```bash
python pipeline/step2_clean.py
```

---

### Step 3: Ekstraksi Informasi
**File**: `step3_extract.py`

Mengekstrak informasi terstruktur (11 kolom) menggunakan GPT-4o-mini.

**Requirements**:
- `OPENAI_API_KEY` environment variable

**Input**: `data/chatbot_food_dataset.csv`
**Output**: `data/chatbot_food_dataset.csv` (+ 11 kolom terstruktur)

**Kolom yang diekstrak**:
- nama_tempat
- lokasi
- kategori_makanan
- tipe_tempat
- range_harga
- menu_andalan
- fasilitas
- jam_buka
- jam_tutup
- hari_operasional
- extracted_hashtags

**Run**:
```bash
python pipeline/step3_extract.py
```

---

### Step 4: Menambahkan Link Lokasi
**File**: `step4_add_links.py`

Matching dengan Google Maps link dari `data/data_link.csv`.

**Requirements**: None

**Input**: 
- `data/chatbot_food_dataset.csv`
- `data/data_link.csv`

**Output**: `data/chatbot_food_dataset.csv` (+ kolom `link_lokasi`)

**Run**:
```bash
python pipeline/step4_add_links.py
```

---

## 🚀 Run All Steps

Gunakan script runner utama:

```bash
python run_pipeline.py
```

**Options**:
```bash
# Run specific step
python run_pipeline.py --step 2

# Skip steps
python run_pipeline.py --skip 1,2

# List all steps
python run_pipeline.py --list
```

## 📊 Features

Semua script memiliki fitur:
- ✅ Auto-save progress
- ✅ Resume capability
- ✅ Retry mechanism (3x)
- ✅ Progress tracking
- ✅ Error handling
- ✅ Rate limiting (untuk API calls)

## 📚 Documentation

Lihat dokumentasi lengkap di `docs/02_PIPELINE_GUIDE.md`

---

**Ready to process! 🚀**
