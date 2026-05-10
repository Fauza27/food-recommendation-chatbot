# Pipeline Scripts

Core executable scripts for the Food Chatbot Dataset ETL pipeline.

## Pipeline Steps

### Step 1: Audio Transcription
**File**: `step1_transcribe.py`

Transcribes Instagram audio into text utilizing Azure Speech Service continuous recognition.

**Requirements**:
- `AZURE_SPEECH_KEY` environment variable
- `AZURE_REGION` environment variable

**Input**: `data/dataset_instagram-scraper_*.csv`
**Output**: `data/transcribed_dataset_*.csv` (+ `raw_transcribe` column)

**Run**:
```bash
python pipeline/step1_transcribe.py
```

---

### Step 2: Transcription Cleaning
**File**: `step2_clean.py`

Performs contextual spell-checking and fixes transcription errors using GPT-4o-mini.

**Requirements**:
- `OPENAI_API_KEY` environment variable

**Input**: `data/transcribed_dataset_*.csv`
**Output**: `data/chatbot_food_dataset.csv` (+ `cleaned_transcribe` column)

**Run**:
```bash
python pipeline/step2_clean.py
```

---

### Step 3: Information Extraction
**File**: `step3_extract.py`

Extracts structured information (11 fields) using GPT-4o-mini JSON mode.

**Requirements**:
- `OPENAI_API_KEY` environment variable

**Input**: `data/chatbot_food_dataset.csv`
**Output**: `data/chatbot_food_dataset.csv` (+ 11 structured columns)

**Extracted columns**:
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

### Step 4: GCP Location Discovery
**File**: `step4_gcp_places.py`

Matches and retrieves accurate Google Maps links using the GCP Places API.

**Requirements**:
- `GCP_MAPS_API_KEY` environment variable

**Input**: `data/chatbot_food_dataset.csv`
**Output**: `data/chatbot_food_dataset.csv` (+ `link_lokasi` column)

**Run**:
```bash
python pipeline/step4_gcp_places.py
```

---

## Run All Steps

Use the main pipeline orchestrator from the root directory:

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

## Features

All pipeline scripts implement the following data engineering best practices:
- Auto-save progress
- Incremental resume capability
- Retry mechanism (3x) for transient faults
- Built-in progress tracking
- Robust error handling
- Rate limiting for external API calls

## Documentation

For an in-depth execution guide, refer to `docs/01_PIPELINE_GUIDE.md`
