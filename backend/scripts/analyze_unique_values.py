import pandas as pd
import numpy as np

def analyze_unique_values(input_file):
    """
    Menganalisis nilai unik dari setiap kolom untuk menemukan pola nilai tidak valid
    """
    print(f"Membaca file: {input_file}\n")
    
    # Baca CSV
    df = pd.read_csv(input_file)
    
    print(f"Total baris: {len(df)}")
    print(f"Total kolom: {len(df.columns)}\n")
    print("="*80)
    
    # Analisis setiap kolom
    for col in df.columns:
        print(f"\n📊 KOLOM: {col}")
        print("-" * 80)
        
        # Hitung nilai null
        null_count = df[col].isnull().sum()
        print(f"Nilai NULL/NaN: {null_count}")
        
        # Hitung nilai unik
        unique_count = df[col].nunique()
        print(f"Jumlah nilai unik: {unique_count}")
        
        # Tampilkan nilai unik (max 30 untuk kolom dengan sedikit nilai unik)
        if unique_count <= 30:
            print(f"\nSemua nilai unik:")
            value_counts = df[col].value_counts(dropna=False)
            for value, count in value_counts.items():
                if pd.isna(value):
                    print(f"  [NULL/NaN]: {count} baris")
                else:
                    print(f"  '{value}': {count} baris")
        else:
            # Untuk kolom dengan banyak nilai unik, tampilkan yang paling sering muncul
            print(f"\n10 nilai paling sering muncul:")
            value_counts = df[col].value_counts(dropna=False).head(10)
            for value, count in value_counts.items():
                if pd.isna(value):
                    print(f"  [NULL/NaN]: {count} baris")
                else:
                    # Potong string panjang
                    display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  '{display_value}': {count} baris")
            
            # Cari nilai yang mencurigakan (mengandung kata kunci tidak valid)
            suspicious_keywords = ['tidak', 'unknown', 'n/a', 'kosong', 'null', 'none', 'empty', '-']
            suspicious_values = []
            
            for value in df[col].unique():
                if pd.notna(value) and isinstance(value, str):
                    value_lower = value.lower().strip()
                    if any(keyword in value_lower for keyword in suspicious_keywords):
                        count = (df[col] == value).sum()
                        suspicious_values.append((value, count))
            
            if suspicious_values:
                print(f"\n⚠️  Nilai mencurigakan ditemukan:")
                for value, count in suspicious_values:
                    print(f"  '{value}': {count} baris")
        
        print()

if __name__ == "__main__":
    input_file = "backend/data/cleaned_enhanced_data_2.csv"
    analyze_unique_values(input_file)
