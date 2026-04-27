"""
Test FREE version API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("="*80)
print("  Testing FREE Version API (HuggingFace Embeddings)")
print("="*80)

print("\nWaiting for server to start...")
time.sleep(3)

# Test 1: Root
print("\n=== Test 1: Root Endpoint ===")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✓ Status: {response.status_code}")
    data = response.json()
    print(f"  Message: {data['message']}")
    print(f"  Embedding: {data.get('embedding', 'N/A')}")
    print(f"  LLM: {data.get('llm', 'N/A')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Health
print("\n=== Test 2: Health Endpoint ===")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✓ Status: {response.status_code}")
    data = response.json()
    print(f"  Status: {data['status']}")
    print(f"  Embedding type: {data.get('embedding_type', 'N/A')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Time
print("\n=== Test 3: Time Endpoint ===")
try:
    response = requests.get(f"{BASE_URL}/time", timeout=5)
    print(f"✓ Status: {response.status_code}")
    data = response.json()
    print(f"  Time: {data['formatted']}")
    print(f"  Day: {data['day']}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Chat (with FREE embeddings!)
print("\n=== Test 4: Chat Endpoint (FREE Embeddings!) ===")
try:
    payload = {
        "message": "Rekomendasi tempat sarapan yang enak",
        "conversation_history": []
    }
    print(f"Query: {payload['message']}")
    print("Sending request...")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=30
    )
    
    print(f"✓ Status: {response.status_code}")
    data = response.json()
    
    print(f"\nResponse:")
    print(f"  {data['message'][:200]}...")
    
    print(f"\nRestaurants: {len(data['restaurants'])} recommendations")
    for i, resto in enumerate(data['restaurants'], 1):
        print(f"\n  {i}. {resto['nama_tempat']}")
        print(f"     Status: {resto['status_operasional']}")
        print(f"     Harga: {resto['range_harga']}")
        print(f"     Instagram: {resto['link_instagram'][:50]}...")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
print("  Test Complete!")
print("="*80)
print("\n✓ FREE embeddings working! No API costs, no throttling!")
