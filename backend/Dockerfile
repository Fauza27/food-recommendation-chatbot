# Gunakan base image Python resmi yang ringan
FROM python:3.11-slim

# Setel direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching yang lebih baik
COPY requirements.txt .

# Install semua dependensi
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin semua kode proyek Anda ke dalam container
# Penting: Pastikan file CSV Anda juga ikut tersalin!
COPY . .

# Cloud Run akan menyediakan environment variable PORT secara otomatis
# Kita tidak perlu mendefinisikannya di sini

# Perintah untuk menjalankan aplikasi FastAPI dengan Uvicorn
# Ini akan berjalan ketika container dimulai
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]