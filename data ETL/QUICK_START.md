# Quick Start Guide

A concise guide to bootstrapping and executing the Food Chatbot ETL Pipeline.

## 3-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env with your text editor
notepad .env
```

Supply your API keys in the `.env` file:
```env
AZURE_SPEECH_KEY=your-azure-key-here
AZURE_REGION=southeastasia
OPENAI_API_KEY=your-openai-key-here
GCP_MAPS_API_KEY=your-gcp-key-here
```

### 3. Run Pipeline

```bash
# Execute all steps sequentially
python run_pipeline.py

# Or execute a specific step
python run_pipeline.py --step 2
```

---

## Commands Cheat Sheet

```bash
# List all pipeline steps
python run_pipeline.py --list

# Run all steps
python run_pipeline.py

# Run specific step (1-4)
python run_pipeline.py --step 1

# Skip specific steps
python run_pipeline.py --skip 1,2

# Verify configuration parsing
python -c "from config import print_config_info; print_config_info()"
```

---

## API Service Requirements

### Azure Speech Service (Free Tier)
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create Speech Service resource
3. Obtain the API Key from "Keys and Endpoint"
4. Note: Free tier provides 5 hours/month

### OpenAI API (Pay-as-you-go)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Ensure billing is enabled
4. Note: Estimated cost is ~$0.35 for 900 records

### Google Cloud Platform (Places API New)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Places API (New)"
3. Generate an API Key under Credentials

---

## Pipeline Architecture Overview

| Step | Script | Core Function | Est. Cost |
|------|--------|---------------|-----------|
| 1 | step1_transcribe.py | Audio → Text via Azure | Free |
| 2 | step2_clean.py | Contextual Error Correction | ~$0.15 |
| 3 | step3_extract.py | Structured JSON Extraction | ~$0.20 |
| 4 | step4_gcp_places.py | Location URI matching | Free |

**Total Est. Cost**: ~$0.35 per 900 rows processed.

---

## Troubleshooting Guide

### Error: Missing Credentials

**Fix**: Ensure your `.env` file is located in the root directory and contains all required variables.

```bash
cp .env.example .env
notepad .env
```

### Error: Audio Processing Failed (FFmpeg)

**Fix**: Ensure `ffmpeg` and `ffprobe` are installed on your system PATH.
- Windows: Download from gyan.dev and add to PATH
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Error: Rate Limit Exceeded (OpenAI)

**Fix**: The pipeline handles rate limit retries automatically. If it still fails, check your OpenAI billing dashboard to ensure you haven't hit your organization's quota.
