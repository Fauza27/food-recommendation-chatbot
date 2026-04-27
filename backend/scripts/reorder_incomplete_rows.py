import pandas as pd
import sys
import numpy as np

def reorder_csv_incomplete_rows(input_file, output_file=None):
    """
    Memindahkan baris dengan nilai kosong/tidak lengkap ke akhir file CSV
    
    Args:
        input_file: Path ke file CSV input
        output_file: Path ke file CSV output (opsional, default: overwrite input)
    """
    print(f"Membaca file: {input_file}")
    
    # Baca CSV
    df = pd.read_csv(input_file)
    
    print(f"Total baris: {len(df)}")
    print(f"Total kolom: {len(df.columns)}")
    
    # Daftar nilai yang dianggap tidak valid/tidak lengkap
    invalid_values = [
        'Tidak Ditemukan',
        'tidak ditemukan',
        'Unknown',
        'unknown',
        'Link tidak tersedia',
        'link tidak tersedia',
        'Tidak tersedia',
        'tidak tersedia',
        'N/A',
        'n/a',
        '-',
        '',
        ' ',
        '[]',  # Array kosong
        "['Unknown']",  # Array dengan Unknown
        "['tidak_relevan']",
        "['unknown']",
        "['tidak ada informasi', 'data tidak lengkap']",
        "['tidak_diketahui']",
        "['tidak relevan']",
        "['tidak_ada_data']",
        "['tidak_relevan', 'bukan_tempat_makan']"
    ]
    
    # Daftar frasa yang menandakan data tidak lengkap
    invalid_phrases = [
        'Data tidak cukup',
        'Tidak ada informasi',
        'Informasi tidak cukup',
        'tidak relevan',
        'tidak ada data',
        'data tidak lengkap'
    ]
    
    # Fungsi untuk mengecek apakah nilai tidak valid
    def is_invalid(value):
        # Cek jika null/NaN
        if pd.isna(value):
            return True
        # Cek jika string kosong atau hanya spasi
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == '' or stripped in invalid_values:
                return True
            # Cek jika mengandung frasa tidak valid
            for phrase in invalid_phrases:
                if phrase.lower() in stripped.lower():
                    return True
        return False
    
    # Identifikasi baris yang memiliki nilai tidak valid
    incomplete_mask = df.apply(lambda row: row.apply(is_invalid).any(), axis=1)
    
    # Pisahkan baris lengkap dan tidak lengkap
    complete_rows = df[~incomplete_mask]
    incomplete_rows = df[incomplete_mask]
    
    print(f"\nBaris lengkap: {len(complete_rows)}")
    print(f"Baris tidak lengkap: {len(incomplete_rows)}")
    
    # Analisis detail kolom yang bermasalah
    if len(incomplete_rows) > 0:
        print("\n=== Analisis Kolom Bermasalah ===")
        for col in df.columns:
            invalid_count = incomplete_rows[col].apply(is_invalid).sum()
            if invalid_count > 0:
                print(f"  {col}: {invalid_count} baris tidak valid")
    
    # Gabungkan kembali: baris lengkap di atas, tidak lengkap di bawah
    df_reordered = pd.concat([complete_rows, incomplete_rows], ignore_index=True)
    
    # Tentukan output file
    if output_file is None:
        output_file = input_file
    
    # Simpan hasil
    df_reordered.to_csv(output_file, index=False)
    print(f"\nFile berhasil disimpan ke: {output_file}")
    
    # Tampilkan beberapa contoh baris tidak lengkap
    if len(incomplete_rows) > 0:
        print("\n=== Contoh baris tidak lengkap (10 pertama) ===")
        for idx, row in incomplete_rows.head(10).iterrows():
            invalid_cols = []
            for col in df.columns:
                if is_invalid(row[col]):
                    invalid_cols.append(f"{col}={row[col]}")
            print(f"Baris {idx}: {', '.join(invalid_cols[:5])}")  # Tampilkan max 5 kolom

if __name__ == "__main__":
    input_file = "backend/data/cleaned_enhanced_data_2.csv"
    
    # Bisa juga simpan ke file baru untuk backup
    # output_file = "backend/data/cleaned_enhanced_data_2_reordered.csv"
    
    reorder_csv_incomplete_rows(input_file)
    print("\n✅ Selesai! Baris tidak lengkap sudah dipindahkan ke akhir.")
