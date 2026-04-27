"""
Manual test examples for new features
Run this with server running to see actual responses
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat(message: str, description: str = ""):
    """Helper function to test chat endpoint"""
    print(f"\n{'='*70}")
    if description:
        print(f"TEST: {description}")
    print(f"Query: '{message}'")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "conversation_history": []},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Status: {response.status_code}")
            print(f"✓ Cards: {len(data.get('restaurants', []))}")
            print(f"\n--- AI Response ---")
            print(data['message'][:500] + "..." if len(data['message']) > 500 else data['message'])
            
            if data.get('restaurants'):
                print(f"\n--- Restaurant Cards ---")
                for i, resto in enumerate(data['restaurants'][:3], 1):
                    print(f"{i}. {resto['nama_tempat']}")
                    print(f"   Status: {resto['status_operasional']}")
                    print(f"   Harga: {resto['range_harga']}")
                    print(f"   Jam: {resto['jam_buka']} - {resto['jam_tutup']}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Server not running!")
        print("Start server with: python src/main.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("="*70)
    print("MANUAL TEST EXAMPLES - New Features")
    print("="*70)
    print("\nMake sure server is running: python src/main.py")
    input("Press Enter to continue...")
    
    # Test 1: Dynamic Count
    print("\n\n" + "="*70)
    print("FEATURE 1: DYNAMIC RECOMMENDATION COUNT")
    print("="*70)
    
    test_chat(
        "Berikan 3 rekomendasi tempat sarapan",
        "Request 3 recommendations"
    )
    
    test_chat(
        "Kasih 7 tempat makan murah",
        "Request 7 recommendations"
    )
    
    test_chat(
        "Rekomendasikan 10 restoran enak",
        "Request 10 recommendations"
    )
    
    # Test 2: Typo Tolerance
    print("\n\n" + "="*70)
    print("FEATURE 2: TYPO TOLERANCE")
    print("="*70)
    
    test_chat(
        "Kasih lma tempat makan enak",
        "Typo: lma → lima (5)"
    )
    
    test_chat(
        "Rekomendasikan tjuh restoran murah",
        "Typo: tjuh → tujuh (7)"
    )
    
    test_chat(
        "Mau dlapan tempat makan",
        "Typo: dlapan → delapan (8)"
    )
    
    # Test 3: Future Time
    print("\n\n" + "="*70)
    print("FEATURE 3: FUTURE TIME RECOMMENDATIONS")
    print("="*70)
    
    test_chat(
        "Rekomendasikan tempat makan besok pagi",
        "Future: besok pagi"
    )
    
    test_chat(
        "Cari restoran besok siang",
        "Future: besok siang"
    )
    
    test_chat(
        "Tempat makan nanti malam",
        "Future: nanti malam"
    )
    
    test_chat(
        "Rekomendasi tempat makan jam 7 malam",
        "Future: jam 7 malam"
    )
    
    # Test 4: Combined Features
    print("\n\n" + "="*70)
    print("FEATURE 4: COMBINED FEATURES")
    print("="*70)
    
    test_chat(
        "Kasih lma tempat makan besok pagi",
        "Combined: typo + future time"
    )
    
    test_chat(
        "Berikan tjuh rekomendasi restoran murah besok siang",
        "Combined: typo + count + future time"
    )
    
    # Summary
    print("\n\n" + "="*70)
    print("MANUAL TEST COMPLETED")
    print("="*70)
    print("\nReview the responses above to verify:")
    print("✓ Correct number of recommendations")
    print("✓ Typo handling works")
    print("✓ Future time context in responses")
    print("✓ Appropriate restaurant cards")

if __name__ == "__main__":
    main()
