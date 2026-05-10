"""
Automated Location Discovery Pipeline.

Utilizes the Google Maps Places API (New) via REST to programmatically 
search and retrieve `googleMapsUri` for records with missing location links.
Implements a Field Mask approach for cost optimization (free tier) and 
a multi-layered retry strategy using varied textual inputs.
"""

import os
import sys
import time
import requests
import pandas as pd
from tqdm import tqdm

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GCP_MAPS_API_KEY, check_gcp_credentials

print("Executing Step 4: GCP Places API Link Discovery")

# Check credentials
if not check_gcp_credentials():
    sys.exit(1)

def search_place_link(query):
    """Search for a place and return its Google Maps URI"""
    if not query or not str(query).strip():
        return None
        
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GCP_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.googleMapsUri"
    }
    data = {
        "textQuery": str(query)
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if "places" in result and len(result["places"]) > 0:
                return result["places"][0].get("googleMapsUri")
        return None
    except Exception as e:
        print(f"Error requesting API: {e}")
        return None

def main():
    dataset_path = 'data/chatbot_food_dataset.csv'
    
    print("Loading dataset...")
    if not os.path.exists(dataset_path):
        print(f"[ERROR] File tidak ditemukan: {dataset_path}")
        sys.exit(1)
        
    df = pd.read_csv(dataset_path)
    
    # Check if 'link_lokasi' exists
    if 'link_lokasi' not in df.columns:
        df['link_lokasi'] = pd.NA
        
    # Get rows where link_lokasi is empty
    empty_links_mask = df['link_lokasi'].isna() | (df['link_lokasi'] == '')
    empty_links_idx = df[empty_links_mask].index
    
    total_empty = len(empty_links_idx)
    print(f"Total baris dengan link kosong: {total_empty}")
    
    if total_empty == 0:
        print("[SUCCESS] Semua baris sudah memiliki link lokasi!")
        return
        
    print(f"Initiating search for {total_empty} rows...")
    print("Strategy: 3-tier fallback query matching.")
    
    success_count = 0
    
    # Process with progress bar
    for idx in tqdm(empty_links_idx, desc="Searching locations"):
        row = df.loc[idx]
        nama_tempat = str(row.get('nama_tempat', '')).strip()
        if nama_tempat == 'nan' or not nama_tempat:
            continue
            
        lokasi = str(row.get('lokasi', '')).strip()
        caption = str(row.get('caption', '')).strip()
        transcribe = str(row.get('cleaned_transcribe', '')).strip()
        
        # Prepare 3 different queries
        queries = []
        
        # Attempt 1: nama_tempat + lokasi
        q1 = f"{nama_tempat} {lokasi if lokasi != 'nan' else ''}".strip()
        queries.append(q1)
        
        # Attempt 2: nama_tempat + caption
        if caption != 'nan' and caption:
            q2 = f"{nama_tempat} {caption[:100]}".strip()
            queries.append(q2)
            
        # Attempt 3: nama_tempat + transcribe
        if transcribe != 'nan' and transcribe:
            q3 = f"{nama_tempat} {transcribe[:100]}".strip()
            queries.append(q3)
            
        link_found = None
        for i, query in enumerate(queries, 1):
            if not query:
                continue
                
            link_found = search_place_link(query)
            
            # Delay to prevent rate limiting (Free tier safety)
            time.sleep(1)
            
            if link_found:
                break
                
        if link_found:
            df.at[idx, 'link_lokasi'] = link_found
            success_count += 1
            
        # Auto-save every 50 success
        if success_count > 0 and success_count % 50 == 0:
            df.to_csv(dataset_path, index=False)
            
    # Final save
    df.to_csv(dataset_path, index=False)
    
    print("STEP 4 COMPLETED: SEARCH RESULTS")
    print(f"Baris diproses: {total_empty}")
    print(f"Berhasil ditemukan: {success_count} ({success_count/total_empty*100:.1f}%)")
    print(f"Masih kosong: {total_empty - success_count}")
    print(f"Dataset telah disimpan di: {dataset_path}")

if __name__ == "__main__":
    main()
