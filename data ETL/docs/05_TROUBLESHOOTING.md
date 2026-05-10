# 05 - Troubleshooting

Solusi untuk masalah umum yang mungkin terjadi saat menjalankan pipeline.

## 🔧 General Issues

### Error: "Module not found"

**Penyebab**: Dependencies belum terinstall

**Solusi**:
```bash
# Install semua dependencies
pip install -r requirements.txt

# Atau install satu per satu
pip install pandas openai azure-cognitiveservices-speech requests tqdm
```

### Error: "Permission denied"

**Penyebab**: File sedang dibuka di program lain (Excel, etc.)

**Solusi**:
1. Tutup semua program yang membuka file CSV
2. Jalankan script lagi

### Error: "File not found"

**Penyebab**: Path file salah atau file tidak ada

**Solusi**:
1. Cek apakah file ada di folder `data/`
2. Pastikan nama file sesuai dengan yang di script
3. Gunakan path relatif dari root project

---

## 🔵 Azure Speech Service Issues

### Error: "Invalid subscription key"

**Penyebab**: API key salah atau belum di-set

**Solusi**:
1. Cek kembali KEY di [Azure Portal](https://portal.azure.com/) → Resource → Keys and Endpoint
2. Pastikan tidak ada spasi di awal/akhir key
3. Set environment variable dengan benar:
   ```bash
   # Windows CMD
   set AZURE_SPEECH_KEY=your-key-here
   
   # Windows PowerShell
   $env:AZURE_SPEECH_KEY="your-key-here"
   
   # Linux/macOS
   export AZURE_SPEECH_KEY=your-key-here
   ```

### Error: "Region mismatch"

**Penyebab**: Region tidak sesuai dengan resource

**Solusi**:
1. Cek region di Azure Portal → Resource → Keys and Endpoint
2. Update environment variable:
   ```bash
   set AZURE_REGION=southeastasia
   ```
3. Region harus lowercase tanpa spasi (contoh: `eastus`, `southeastasia`)

### Error: "Quota exceeded"

**Penyebab**: Sudah melebihi 5 jam free tier bulan ini

**Solusi**:
1. Tunggu bulan berikutnya (quota reset setiap bulan)
2. Atau upgrade ke paid tier
3. Cek usage di Azure Portal → Resource → Metrics

### Error: "Connection timeout"

**Penyebab**: Koneksi internet lambat atau tidak stabil

**Solusi**:
1. Cek koneksi internet
2. Coba lagi beberapa saat
3. Script otomatis retry 3x per audio

### Error: "Audio format not supported"

**Penyebab**: Format audio tidak didukung atau corrupt

**Solusi**:
1. Pastikan ffmpeg terinstall
2. Script otomatis konversi ke WAV
3. Jika masih error, skip audio tersebut

---

## 🟢 OpenAI API Issues

### Error: "Incorrect API key provided"

**Penyebab**: API key salah atau tidak valid

**Solusi**:
1. Cek kembali API key di [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Pastikan tidak ada spasi di awal/akhir
3. Key harus dimulai dengan `sk-` atau `sk-proj-`
4. Set environment variable:
   ```bash
   set OPENAI_API_KEY=sk-proj-your-key-here
   ```
5. Buat key baru jika perlu

### Error: "You exceeded your current quota"

**Penyebab**: 
- Belum add payment method, atau
- Sudah melebihi spending limit

**Solusi**:
1. Add payment method di [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Atau naikkan spending limit
3. Cek usage di [Usage Dashboard](https://platform.openai.com/usage)

### Error: "Rate limit exceeded"

**Penyebab**: Terlalu banyak request dalam waktu singkat

**Solusi**:
1. Script sudah ada rate limiting (1s delay)
2. Tunggu beberapa menit
3. Jalankan script lagi (otomatis resume)

### Error: "Invalid JSON response"

**Penyebab**: GPT response tidak valid JSON

**Solusi**:
1. Script otomatis retry 3x
2. Jika masih error, row akan di-skip
3. Bisa di-process manual nanti

### Error: "Context length exceeded"

**Penyebab**: Input text terlalu panjang

**Solusi**:
1. Script sudah limit max_tokens
2. Jika masih error, potong input text
3. Atau skip row tersebut

---

## 📊 Data Processing Issues

### Issue: "Progress stuck at X%"

**Penyebab**: Script sedang memproses row yang lama

**Solusi**:
1. Tunggu - beberapa row memang lebih lama
2. Cek console untuk error message
3. Jika stuck >5 menit, Ctrl+C dan restart (otomatis resume)

### Issue: "Some rows skipped"

**Penyebab**: Row tidak memenuhi kriteria atau error

**Solusi**:
1. Cek console output untuk detail
2. Row dengan whitespace-only akan di-skip (normal)
3. Row dengan error akan di-skip setelah 3x retry
4. Bisa di-process manual nanti

### Issue: "Output file not updated"

**Penyebab**: Auto-save belum triggered

**Solusi**:
1. Script auto-save setiap 5-10 rows
2. Tunggu sampai batch berikutnya
3. Atau stop script (Ctrl+C) untuk force save

### Issue: "Duplicate rows in output"

**Penyebab**: Script dijalankan multiple times tanpa resume

**Solusi**:
1. Hapus output file
2. Jalankan script dari awal
3. Atau gunakan pandas untuk remove duplicates:
   ```python
   import pandas as pd
   df = pd.read_csv('data/chatbot_food_dataset.csv')
   df = df.drop_duplicates()
   df.to_csv('data/chatbot_food_dataset.csv', index=False)
   ```

---

## 🔄 Resume & Recovery Issues

### Issue: "Resume not working"

**Penyebab**: Output file corrupt atau tidak ada

**Solusi**:
1. Cek apakah output file ada
2. Cek apakah file bisa dibuka dengan pandas
3. Jika corrupt, restore dari backup atau mulai dari awal

### Issue: "Want to restart from beginning"

**Solusi**:
1. Hapus atau rename output file
2. Jalankan script lagi
3. Atau gunakan backup file:
   ```bash
   # Windows
   del data\chatbot_food_dataset.csv
   
   # Linux/macOS
   rm data/chatbot_food_dataset.csv
   ```

---

## 💰 Cost & Usage Issues

### Issue: "Biaya lebih tinggi dari estimasi"

**Penyebab**: 
- Lebih banyak tokens digunakan
- Retry mechanism
- Input text lebih panjang

**Solusi**:
1. Cek usage di dashboard
2. Set spending limit lebih rendah
3. Optimize prompt untuk less tokens

### Issue: "Want to reduce costs"

**Solusi**:
1. **Gunakan GPT-4o-mini** (sudah digunakan)
2. **Batch processing** - proses banyak rows sekaligus
3. **Lower temperature** - less random = less tokens
4. **Limit max_tokens** - set lebih rendah
5. **Cache hasil** - jangan re-process yang sudah ada

---

## 🐛 Script-Specific Issues

### batch_transcribe_csv.py

**Issue**: "No audio URL found"

**Solusi**:
- Normal untuk beberapa rows
- Script otomatis skip dan mark sebagai "[NO AUDIO URL]"

**Issue**: "Silent video detected"

**Solusi**:
- Normal untuk Instagram Reels dengan musik overlay
- Script otomatis mark sebagai "[NO AUDIO: Silent Video]"

### clean_transcriptions_gpt.py

**Issue**: "Whitespace-only rows skipped"

**Solusi**:
- Normal behavior
- Rows tanpa text akan di-skip
- Tidak perlu di-clean

### extract_structured_info.py

**Issue**: "Some fields empty"

**Solusi**:
- Normal jika info tidak ada di text
- Script set fallback values
- Bisa di-fill manual nanti

### add_link_lokasi.py

**Issue**: "Many rows not matched"

**Solusi**:
- Normal jika data_link.csv tidak lengkap
- 78.4% match rate sudah bagus
- Bisa scrape Google Maps untuk yang missing

---

## 🔍 Debugging Tips

### 1. Enable Verbose Logging

Edit script dan tambahkan:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Test with Small Sample

```python
# Test dengan 10 rows pertama
df = pd.read_csv('input.csv', nrows=10)
```

### 3. Check Data Types

```python
import pandas as pd
df = pd.read_csv('data/chatbot_food_dataset.csv')
print(df.dtypes)
print(df.info())
```

### 4. Inspect Problematic Rows

```python
# Cek rows dengan missing data
missing = df[df['cleaned_transcribe'].isna()]
print(missing[['url', 'raw_transcribe']])
```

### 5. Validate Output

```python
# Cek completeness
print(f"Total rows: {len(df)}")
print(f"Non-null cleaned_transcribe: {df['cleaned_transcribe'].notna().sum()}")
print(f"Non-null nama_tempat: {df['nama_tempat'].notna().sum()}")
```

---

## 🆘 Still Having Issues?

### Check These First

1. ✅ Dependencies installed (`pip install -r requirements.txt`)
2. ✅ Environment variables set (AZURE_SPEECH_KEY, OPENAI_API_KEY)
3. ✅ Input files exist in `data/` folder
4. ✅ Internet connection stable
5. ✅ API keys valid and have quota

### Get Help

1. **Check console output** - Error messages biasanya jelas
2. **Read error message carefully** - Sering ada hint solusi
3. **Check API status**:
   - Azure: [status.azure.com](https://status.azure.com/)
   - OpenAI: [status.openai.com](https://status.openai.com/)
4. **Search error message** - Google/Stack Overflow
5. **Check documentation**:
   - Azure: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
   - OpenAI: [platform.openai.com/docs](https://platform.openai.com/docs)

### Common Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check environment variables (Windows)
set

# Check environment variables (Linux/macOS)
env

# Test pandas
python -c "import pandas; print(pandas.__version__)"

# Test OpenAI
python -c "import openai; print(openai.__version__)"

# Test Azure
python -c "import azure.cognitiveservices.speech; print('OK')"
```

---

## 📚 Related Documentation

- Main README: `01_README.md`
- Pipeline Guide: `02_PIPELINE_GUIDE.md`
- Setup Guide: `03_SETUP_GUIDE.md`
- Dataset Info: `04_DATASET_INFO.md`

---

**Good luck! 🍀**

Jika masih ada masalah, coba restart dari awal atau contact support.
