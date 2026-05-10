# Food Chatbot Dataset Pipeline

Complete pipeline untuk memproses dataset Instagram menjadi dataset chatbot yang siap digunakan.

## �� Quick Start

```bash
# 1. Set credentials
export AZURE_SPEECH_KEY="your-azure-key"
export AZURE_REGION="southeastasia"
export OPENAI_API_KEY="your-openai-key"

# 2. Run pipeline
python run_pipeline.py

# 3. Check output
ls data/chatbot_food_dataset.csv
```

## 📊 What This Pipeline Does

Transforms raw Instagram data into structured chatbot dataset through 4 steps:

1. **Transcription** (Azure Speech) - Audio → Text
2. **Cleaning** (GPT-4o-mini) - Fix typos & punctuation  
3. **Extraction** (GPT-4o-mini) - Extract structured data
4. **Link Lokasi** - Add Google Maps links

**Input**: 900 Instagram posts (raw data)
**Output**: 900 rows × 34 columns (structured data)

## 💰 Cost & Time

- **Cost**: ~$0.40 (Rp 6,400)
- **Time**: ~18 hours
- **Quality**: ⭐⭐⭐⭐⭐ (91.8% success rate)

## 📁 Project Structure

```
.
├── docs/
│   ├── 01_README.md           # This file
│   ├── 02_PIPELINE_GUIDE.md   # Complete guide
│   ├── 03_SETUP_GUIDE.md      # Setup instructions
│   └── 04_DATASET_INFO.md     # Dataset documentation
│
├── run_pipeline.py            # Main pipeline runner ⭐
├── clean_transcriptions_gpt.py
├── extract_structured_info.py
├── add_link_lokasi.py
│
├── scripts/
│   └── batch_transcribe_csv.py
│
└── data/
    ├── chatbot_food_dataset.csv  # Final output ⭐
    └── data_link.csv
```

## 📖 Documentation

- **02_PIPELINE_GUIDE.md** - Complete pipeline documentation
- **03_SETUP_GUIDE.md** - Setup Azure & OpenAI credentials
- **04_DATASET_INFO.md** - Dataset columns & statistics

## ✅ Features

- ✅ Fully automated pipeline
- ✅ Resume capability (can continue from errors)
- ✅ Progress tracking & auto-save
- ✅ Cost estimation
- ✅ Production ready

## 🎯 Results

- **900 rows** processed
- **91.8%** transcription success
- **97.4%** cleaning success
- **78.4%** location links matched
- **34 columns** structured data

## 🆘 Need Help?

1. Read **02_PIPELINE_GUIDE.md** for complete guide
2. Read **03_SETUP_GUIDE.md** for setup instructions
3. Check **04_DATASET_INFO.md** for dataset info

---

**Status**: ✅ Production Ready  
**Version**: 2.0  
**Last Updated**: May 2026
