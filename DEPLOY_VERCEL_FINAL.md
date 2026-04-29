# 🚀 Deploy Frontend ke Vercel - FINAL SOLUTION

## Masalah Terakhir

Error: `cd: frontend: No such file or directory`

**Penyebab:** Ada 2 `vercel.json` yang conflict (di root dan di frontend/).

**Solusi:** Saya sudah hapus `vercel.json` di root dan fix yang di `frontend/`.

## ✅ LANGKAH DEPLOY (PASTI BERHASIL)

### Step 1: Push Changes ke GitHub

```bash
git add .
git commit -m "fix: remove conflicting vercel.json"
git push
```

### Step 2: Set Root Directory di Vercel Dashboard

**INI STEP PALING PENTING!**

1. Buka: https://vercel.com/dashboard
2. Pilih project Anda: `food-recommendation-chatbot`
3. Klik **Settings** (di menu atas)
4. Klik **General** (di sidebar kiri)
5. Scroll ke bagian **Root Directory**
6. Klik tombol **Edit**
7. Ketik: `frontend` (tanpa slash)
8. Klik **Save**

**Screenshot untuk referensi:**
```
Root Directory
The directory within your project, in which your code is located.
Leave this field empty if your code is located in the root directory.

[Edit] → Ketik: frontend → [Save]
```

### Step 3: Tambahkan Environment Variable

Masih di Settings:

1. Klik **Environment Variables** (di sidebar kiri)
2. Klik **Add New** atau **Add**
3. Isi form:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://your-backend-url.com` (GANTI dengan URL backend Anda!)
   - **Environments:** Centang **Production**, **Preview**, **Development**
4. Klik **Save**

### Step 4: Redeploy

1. Klik tab **Deployments** (di menu atas)
2. Klik deployment terakhir (yang failed)
3. Klik tombol **"..."** (three dots di kanan atas)
4. Pilih **Redeploy**
5. **PENTING:** **UNCHECK** "Use existing Build Cache"
6. Klik **Redeploy**

### Step 5: Tunggu & Monitor

Build akan jalan ~2-3 menit. Monitor di build logs.

**Expected Success Output:**
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization

Build Completed in /vercel/path0/.next
```

## 🎯 Verifikasi Deployment

Setelah deploy success:

1. **Buka URL:** `https://your-app.vercel.app`
2. **Test homepage:** Harus muncul chat interface
3. **Test explore:** `https://your-app.vercel.app/explore`
4. **Test API:** Coba chat atau search restaurant

## ❌ Jika Masih Gagal

### Cek Build Logs

Di Vercel deployment page, cek:
1. Apakah install command jalan di folder yang benar?
2. Apakah ada error spesifik?

### Cek Root Directory Setting

Pastikan di Settings → General → Root Directory = `frontend` (bukan `./frontend` atau `/frontend`)

### Alternative: Deploy Ulang dari Awal

Jika masih error, coba import ulang:

1. **Hapus project** di Vercel (Settings → General → Delete Project)
2. **Import ulang:**
   - Klik **Add New** → **Project**
   - Pilih repository: `food-recommendation-chatbot`
   - **Root Directory:** Ketik `frontend`
   - **Framework Preset:** Next.js (auto-detect)
   - **Environment Variables:** Tambahkan `NEXT_PUBLIC_API_URL`
   - Klik **Deploy**

## 🆘 Troubleshooting Spesifik

### Error: "Module not found"

**Solusi:** Root Directory belum di-set. Ulangi Step 2.

### Error: "cd: frontend: No such file or directory"

**Solusi:** Ada `vercel.json` di root yang conflict. Saya sudah hapus, push ke GitHub.

### Error: "NEXT_PUBLIC_API_URL is not defined"

**Solusi:** Environment variable belum ditambahkan. Ulangi Step 3.

### Build Success tapi Halaman Blank

**Solusi:** 
1. Cek browser console untuk error
2. Pastikan `NEXT_PUBLIC_API_URL` benar
3. Test backend URL langsung di browser

## 📋 Final Checklist

- [ ] Push changes ke GitHub (vercel.json di root sudah dihapus)
- [ ] Root Directory di Vercel = `frontend`
- [ ] Environment Variable `NEXT_PUBLIC_API_URL` sudah ditambahkan
- [ ] Redeploy tanpa build cache
- [ ] Build logs menunjukkan success
- [ ] Test homepage bisa dibuka
- [ ] Test API connection (chat/search)

## 💡 Pro Tips

1. **Selalu set Root Directory** untuk monorepo
2. **Environment variables** harus diawali `NEXT_PUBLIC_` untuk client-side
3. **Clear build cache** jika ada perubahan config
4. **Test backend URL** dulu sebelum deploy frontend

---

## 🎬 Video Tutorial (Jika Perlu)

Jika masih bingung, saya bisa guide step-by-step via:
1. Screenshot setiap step
2. Share screen (jika ada tools)
3. Detailed explanation untuk setiap error

---

**Saya yakin dengan langkah-langkah di atas, deployment akan berhasil!** 🚀

Silakan coba dan share hasilnya (success atau error message).
