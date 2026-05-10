# Food Chatbot Dataset - ETL Pipeline

Data Engineering pipeline designed to extract, transform, and load (ETL) Instagram food review data into a structured dataset for chatbot training.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment variables
cp .env.example .env
# Edit .env and supply your API keys

# 3. Execute pipeline
python run_pipeline.py
```

**IMPORTANT**: You must configure the `.env` file with the appropriate API keys before running. Refer to `docs/06_ENV_SETUP.md` for complete guidelines.

## Dataset

**Output**: `data/chatbot_food_dataset.csv`

- **900 rows** × **34 columns**
- **97.4%** completeness rate
- **Ready for Chatbot LLM Training/RAG**

## Pipeline Architecture

1. **Audio Transcription** - Azure Speech Service (Continuous Recognition)
2. **Transcription Cleaning** - OpenAI GPT-4o-mini
3. **Structured Information Extraction** - OpenAI GPT-4o-mini
4. **Location Discovery** - Google Cloud Platform (Places API New)

## Documentation

Full documentation is available in the `docs/` directory:

1. **[01_README.md](docs/01_README.md)** - Comprehensive project overview
2. **[02_PIPELINE_GUIDE.md](docs/02_PIPELINE_GUIDE.md)** - Pipeline execution guide
3. **[03_SETUP_GUIDE.md](docs/03_SETUP_GUIDE.md)** - Azure & OpenAI service setup
4. **[04_DATASET_INFO.md](docs/04_DATASET_INFO.md)** - Dataset structure & statistics
5. **[05_TROUBLESHOOTING.md](docs/05_TROUBLESHOOTING.md)** - Common issues & solutions
6. **[06_ENV_SETUP.md](docs/06_ENV_SETUP.md)** - Environment variables setup

## Technical Features

- Incremental state saving and resume capabilities
- Resilient retry mechanisms for HTTP/API failures
- Progress tracking via standard CLI utilities
- Cost estimation models
- Standardized error handling and logging
- Built-in rate limiting compliance

## Project Structure

```
data ETL/
├── docs/                          # Comprehensive documentation
│   ├── 00_CLEANUP_REPORT.md
│   ├── 01_README.md
│   ├── ...
│
├── pipeline/                      # Core ETL pipeline stages
│   ├── step1_transcribe.py
│   ├── step2_clean.py
│   ├── step3_extract.py
│   ├── step4_gcp_places.py
│   └── README.md
│
├── data/                          # Datasets
│   ├── chatbot_food_dataset.csv   # Final structured output
│   └── example_*.csv              # Mock data for public portfolio
│
├── scripts/                       # Utilities and helper scripts
│   ├── instagram_downloader.py
│   ├── create_example_data.py
│   └── README.md
│
├── run_pipeline.py                # Main orchestrator
└── requirements.txt               # Dependencies
```

## Requirements

- Python 3.8+
- Azure Speech Service API Key
- OpenAI API Key
- GCP Maps API Key
- FFmpeg (for local audio processing)

## Usage Examples

### Run Full Pipeline
```bash
python run_pipeline.py
```

### Execute Specific Stage
```bash
python run_pipeline.py --step 2
```

### Skip Specific Stages
```bash
python run_pipeline.py --skip 1,2
```

### List Available Stages
```bash
python run_pipeline.py --list
```

## License

Internal project - @jalanmakanenak
