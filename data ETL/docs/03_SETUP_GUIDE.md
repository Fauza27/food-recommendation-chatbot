# 03 - Setup Guide

Panduan lengkap setup Azure Speech Service dan OpenAI API untuk pipeline.

## 📋 Requirements

Pipeline ini membutuhkan 2 service:

1. **Azure Speech Service** - Untuk transkripsi audio (Step 1)
2. **OpenAI API** - Untuk cleaning dan ekstraksi (Step 2 & 3)

---

## 🔵 Azure Speech Service Setup

### Free Tier Limits

- **5 jam audio per bulan** - GRATIS selamanya
- **$200 kredit** untuk new customers (30 hari)
- Setelah free tier: $1 per jam audio

### Langkah Setup

#### 1. Buat Azure Account

1. Kunjungi [Azure Portal](https://portal.azure.com/)
2. Sign in atau buat account baru
3. Jika baru pertama kali, Anda akan mendapat **$200 kredit gratis** (30 hari)

#### 2. Buat Speech Service Resource

1. Di Azure Portal, klik **"Create a resource"**
2. Search **"Speech"** atau pilih **AI + Machine Learning** → **Speech**
3. Klik **"Create"**

#### 3. Konfigurasi Resource

Isi form dengan detail berikut:

**Basics:**
- **Subscription**: Pilih subscription Anda
- **Resource group**: Buat baru atau pilih existing (contoh: `speech-resources`)
- **Region**: Pilih region terdekat (contoh: `Southeast Asia`, `East US`)
- **Name**: Beri nama unik (contoh: `my-speech-service`)
- **Pricing tier**: Pilih **Free F0** (5 jam/bulan gratis)

**Network:**
- Biarkan default (All networks)

**Identity:**
- Biarkan default

**Tags:**
- Optional, bisa dikosongkan

4. Klik **"Review + create"**
5. Klik **"Create"**
6. Tunggu deployment selesai (1-2 menit)

#### 4. Dapatkan Keys dan Region

1. Setelah deployment selesai, klik **"Go to resource"**
2. Di menu kiri, klik **"Keys and Endpoint"**
3. Anda akan melihat:
   - **KEY 1** dan **KEY 2** (copy salah satu)
   - **Location/Region** (contoh: `eastus`, `southeastasia`)
   - **Endpoint** (tidak diperlukan untuk SDK)

4. **SIMPAN KEY DAN REGION INI!**

#### 5. Set Environment Variables

**Windows CMD:**
```cmd
set AZURE_SPEECH_KEY=paste-key-anda-disini
set AZURE_REGION=southeastasia
```

**Windows PowerShell:**
```powershell
$env:AZURE_SPEECH_KEY="paste-key-anda-disini"
$env:AZURE_REGION="southeastasia"
```

**Linux/macOS:**
```bash
export AZURE_SPEECH_KEY=paste-key-anda-disini
export AZURE_REGION=southeastasia
```

**Contoh:**
```bash
AZURE_SPEECH_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
AZURE_REGION=southeastasia
```

### Install Dependencies

```bash
pip install azure-cognitiveservices-speech requests
```

### Install FFmpeg (Diperlukan)

**Windows:**
```bash
choco install ffmpeg
# atau
scoop install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
```

**macOS:**
```bash
brew install ffmpeg
```

### Monitoring Usage

Untuk memantau penggunaan free tier:

1. Buka [Azure Portal](https://portal.azure.com/)
2. Buka Speech resource Anda
3. Klik **"Metrics"** di menu kiri
4. Pilih metric: **"Audio Seconds Transcribed"**
5. Lihat usage dalam detik (5 jam = 18,000 detik)

### Supported Languages

Azure Speech Service support 100+ bahasa, termasuk:

- **Indonesia**: `id-ID`
- **English (US)**: `en-US`
- **English (UK)**: `en-GB`
- **Mandarin**: `zh-CN`
- **Japanese**: `ja-JP`
- **Korean**: `ko-KR`
- **Thai**: `th-TH`
- **Vietnamese**: `vi-VN`

[Lihat daftar lengkap](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

### Referensi

- [Azure Speech Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/)
- [Python SDK Reference](https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/)

---

## 🟢 OpenAI API Setup

### Pricing

- **Tidak ada free tier** - Pay-as-you-go
- **GPT-4o-mini**: $0.150 per 1M input tokens, $0.600 per 1M output tokens
- **Whisper API**: $0.006 per menit audio

### Estimasi Biaya Pipeline

| Tahapan | Model | Biaya (900 rows) |
|---------|-------|------------------|
| Step 2: Cleaning | GPT-4o-mini | ~$0.15 |
| Step 3: Ekstraksi | GPT-4o-mini | ~$0.20 |
| **TOTAL** | | **~$0.35** (~Rp 5,600) |

### Langkah Setup

#### 1. Buat OpenAI Account

1. Kunjungi [OpenAI Platform](https://platform.openai.com/)
2. Sign up atau login
3. Verifikasi email Anda

#### 2. Add Payment Method

⚠️ **PENTING**: OpenAI API memerlukan payment method aktif

1. Buka [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Klik **"Add payment method"**
3. Masukkan kartu kredit/debit Anda
4. Set **spending limit** untuk kontrol budget (opsional tapi direkomendasikan)

**Tips**: Set spending limit $5-10 untuk awal, bisa dinaikkan nanti

#### 3. Dapatkan API Key

1. Buka [API Keys](https://platform.openai.com/api-keys)
2. Klik **"Create new secret key"**
3. Beri nama (contoh: `food-chatbot-pipeline`)
4. **COPY KEY SEKARANG** - tidak bisa dilihat lagi setelah ditutup!
5. Key format: `sk-proj-...` atau `sk-...`

#### 4. Set Environment Variables

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-proj-paste-key-anda-disini
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="sk-proj-paste-key-anda-disini"
```

**Linux/macOS:**
```bash
export OPENAI_API_KEY=sk-proj-paste-key-anda-disini
```

**Contoh:**
```bash
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

### Install Dependencies

```bash
pip install openai
```

### Monitoring Usage & Costs

#### Cek Usage Real-time

1. Buka [Usage Dashboard](https://platform.openai.com/usage)
2. Filter by model (GPT-4o-mini)
3. Lihat usage per hari/bulan

#### Set Budget Alerts

1. Buka [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Set **"Usage limits"**
3. Set **"Email notifications"** untuk alert

### Tips Menghemat Biaya

1. **Gunakan GPT-4o-mini** - 60x lebih murah dari GPT-4
2. **Set temperature rendah** - Lebih konsisten, less tokens
3. **Limit max_tokens** - Hindari response terlalu panjang
4. **Batch processing** - Proses banyak rows sekaligus
5. **Cache hasil** - Simpan hasil untuk avoid re-processing

### Referensi

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Pricing](https://openai.com/api/pricing/)
- [API Reference](https://platform.openai.com/docs/api-reference/)

---

## 🔐 Security Best Practices

### 1. Jangan Commit API Keys

Tambahkan ke `.gitignore`:

```
# API Keys
.env
credentials/
*.key
```

### 2. Gunakan Environment Variables

Jangan hardcode keys di script:

```python
# ❌ JANGAN
OPENAI_API_KEY = "sk-proj-abc123..."

# ✅ LAKUKAN
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### 3. Rotate Keys Secara Berkala

- Azure: Generate key baru di portal, update script, delete key lama
- OpenAI: Create key baru, update script, revoke key lama

### 4. Set Spending Limits

- Azure: Set budget alerts di Cost Management
- OpenAI: Set hard/soft limits di Billing Settings

### 5. Monitor Usage

- Cek usage dashboard secara berkala
- Set up email alerts untuk unusual activity

---

## ✅ Verification

### Test Azure Speech Service

```bash
python -c "import azure.cognitiveservices.speech as speechsdk; print('Azure SDK OK')"
```

### Test OpenAI API

```bash
python -c "import openai; print('OpenAI SDK OK')"
```

### Test Environment Variables

```bash
# Windows CMD
echo %AZURE_SPEECH_KEY%
echo %AZURE_REGION%
echo %OPENAI_API_KEY%

# Windows PowerShell
echo $env:AZURE_SPEECH_KEY
echo $env:AZURE_REGION
echo $env:OPENAI_API_KEY

# Linux/macOS
echo $AZURE_SPEECH_KEY
echo $AZURE_REGION
echo $OPENAI_API_KEY
```

---

## 🆘 Butuh Bantuan?

Lihat `05_TROUBLESHOOTING.md` untuk solusi masalah umum.

**Azure Support:**
- [Azure Speech FAQ](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/faq-stt)
- [Azure Support](https://azure.microsoft.com/en-us/support/)

**OpenAI Support:**
- [OpenAI Help Center](https://help.openai.com/)
- [Community Forum](https://community.openai.com/)
- [API Status](https://status.openai.com/)

---

**Setup Complete! 🎉**

Next: Lihat `02_PIPELINE_GUIDE.md` untuk menjalankan pipeline.
