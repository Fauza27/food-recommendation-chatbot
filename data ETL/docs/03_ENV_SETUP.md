# 06 - Environment Variables Setup

Panduan setup file `.env` untuk keamanan API keys.

## 🔐 Mengapa Menggunakan .env?

**Keuntungan**:
- API keys tidak ter-commit ke Git
- Lebih aman dari hardcoded keys
- Mudah di-manage per environment
- Best practice untuk production

**Sebelum** ( Tidak aman):
```python
OPENAI_API_KEY = "sk-proj-abc123..." # Hardcoded!
```

**Sesudah** ( Aman):
```python
from config import OPENAI_API_KEY # Loaded from .env
```

---

## Quick Setup

### 1. Copy Template

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

### 2. Edit File .env

Buka file `.env` dengan text editor dan isi dengan API keys Anda:

```env
# Azure Speech Service Configuration
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_REGION=southeastasia

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=500
```

### 3. Install Dependencies

```bash
pip install python-dotenv
# atau
pip install -r requirements.txt
```

### 4. Verify

```bash
python -c "from config import check_azure_credentials, check_openai_credentials; check_azure_credentials(); check_openai_credentials()"
```

---

## Environment Variables

### Azure Speech Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_SPEECH_KEY` | Yes | - | Azure Speech Service API key |
| `AZURE_REGION` | Yes | `southeastasia` | Azure region (e.g., eastus, southeastasia) |

**Cara mendapatkan**:
1. Buka [Azure Portal](https://portal.azure.com/)
2. Buka Speech Service resource Anda
3. Klik "Keys and Endpoint"
4. Copy KEY 1 atau KEY 2

### OpenAI API

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `OPENAI_TEMPERATURE` | No | `0.3` | Temperature (0-1) |
| `OPENAI_MAX_TOKENS` | No | `500` | Max tokens per response |

**Cara mendapatkan**:
1. Buka [OpenAI Platform](https://platform.openai.com/)
2. Klik "API Keys"
3. Klik "Create new secret key"
4. Copy key (format: `sk-proj-...`)

---

## Cara Menggunakan

### Dalam Script Python

```python
# Import dari config.py
from config import AZURE_SPEECH_KEY, AZURE_REGION, OPENAI_API_KEY

# Atau langsung dari os.getenv
import os
from dotenv import load_dotenv

load_dotenv()
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
```

### Check Credentials

```python
from config import check_azure_credentials, check_openai_credentials

# Check Azure
if check_azure_credentials():
 print(" Azure credentials OK")

# Check OpenAI
if check_openai_credentials():
 print(" OpenAI credentials OK")
```

### Print Config Info

```python
from config import print_config_info

print_config_info()
# Output:
# Configuration:
# Azure Region: southeastasia
# Azure Key: Set
# OpenAI Key: Set
# OpenAI Model: gpt-4o-mini
# Temperature: 0.3
# Max Tokens: 500
```

---

## 🔒 Security Best Practices

### 1. Jangan Commit .env

File `.env` sudah ada di `.gitignore`:

```gitignore
# API Keys
.env
*.key
```

**Verify**:
```bash
git status
# .env should NOT appear in untracked files
```

### 2. Gunakan .env.example

Commit `.env.example` sebagai template (tanpa API keys):

```env
# .env.example
AZURE_SPEECH_KEY=your-azure-speech-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Rotate Keys Secara Berkala

- Azure: Generate key baru di portal, update .env, delete key lama
- OpenAI: Create key baru, update .env, revoke key lama

### 4. Set Permissions

**Linux/macOS**:
```bash
chmod 600 .env # Only owner can read/write
```

**Windows**:
```powershell
icacls .env /inheritance:r /grant:r "$env:USERNAME:R"
```

### 5. Jangan Share .env

- Jangan kirim via email/chat
- Jangan screenshot
- Jangan paste di public forum
- Share .env.example saja

---

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY tidak ditemukan"

**Penyebab**: File .env tidak ada atau tidak ter-load

**Solusi**:
1. Pastikan file `.env` ada di root project
2. Pastikan format benar (no quotes, no spaces around =)
3. Restart terminal/IDE setelah edit .env

```bash
# Check if .env exists
ls -la .env

# Check content (be careful!)
cat .env
```

### Error: "python-dotenv not found"

**Penyebab**: Package belum terinstall

**Solusi**:
```bash
pip install python-dotenv
```

### Keys Tidak Ter-load

**Penyebab**: Format .env salah

**Format yang benar**:
```env
# CORRECT
AZURE_SPEECH_KEY=abc123xyz
OPENAI_API_KEY=sk-proj-abc123

# WRONG (no quotes!)
AZURE_SPEECH_KEY="abc123xyz"
OPENAI_API_KEY='sk-proj-abc123'

# WRONG (no spaces!)
AZURE_SPEECH_KEY = abc123xyz
```

### Environment Variables vs .env

Jika set environment variable DAN .env, mana yang dipakai?

**Priority**:
1. Environment variable (highest)
2. .env file
3. Default value (lowest)

```python
# Environment variable wins
os.environ["OPENAI_API_KEY"] = "from-env"
# .env has: OPENAI_API_KEY=from-file
# Result: "from-env" is used
```

---

## File Structure

```
data ETL/
├── .env # Your API keys (NOT in Git)
├── .env.example # Template (in Git)
├── config.py # Config loader
├── .gitignore # Includes .env
└── pipeline/
 ├── step1_transcribe.py # Uses config
 ├── step2_clean.py # Uses config
 └── step3_extract.py # Uses config
```

---

## Example .env File

```env
# Azure Speech Service Configuration
# Get from: https://portal.azure.com/
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_REGION=southeastasia

# OpenAI API Configuration
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=500
```

** IMPORTANT**: Ini contoh saja! Jangan gunakan keys ini, generate keys Anda sendiri!

---

## 📖 Related Documentation

- Setup Guide: `03_SETUP_GUIDE.md`
- Pipeline Guide: `02_PIPELINE_GUIDE.md`
- Troubleshooting: `05_TROUBLESHOOTING.md`

---

**Keep your keys safe! 🔐**
