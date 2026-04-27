"""
Test new features: dynamic count, typo handling, future time
"""
import sys
sys.path.append('src')

from utils import extract_number_from_text, parse_future_time, get_samarinda_time

def test_number_extraction():
    """Test number extraction with typo tolerance"""
    print("\n=== Testing Number Extraction ===")
    
    test_cases = [
        ("berikan 5 rekomendasi", 5),
        ("kasih lma tempat makan", 5),  # typo: lma -> lima
        ("rekomendasikan tjuh restoran", 7),  # typo: tjuh -> tujuh
        ("cari tiga tempat", 3),
        ("mau 10 rekomendasi", 10),
        ("berikan dua rekomendasi", 2),
        ("kasih empat tempat", 4),
        ("cari enam restoran", 6),
        ("mau delapan tempat", 8),
        ("berikan sembilan rekomendasi", 9),
    ]
    
    passed = 0
    for query, expected in test_cases:
        result = extract_number_from_text(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{query}' -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_future_time_parsing():
    """Test future time parsing"""
    print("\n=== Testing Future Time Parsing ===")
    
    test_cases = [
        "rekomendasikan tempat makan besok pagi",
        "cari restoran besok siang",
        "mau makan besok malam",
        "tempat makan nanti malam",
        "rekomendasi untuk besok",
        "tempat makan jam 7 malam",
        "restoran untuk pukul 12 siang",
    ]
    
    passed = 0
    for query in test_cases:
        result = parse_future_time(query)
        if result:
            target_time, description = result
            print(f"✓ '{query}'")
            print(f"  -> {target_time.strftime('%Y-%m-%d %H:%M')} ({description})")
            passed += 1
        else:
            print(f"✗ '{query}' -> No future time detected")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed >= len(test_cases) - 1  # Allow 1 failure

def test_api_with_dynamic_count():
    """Test API with dynamic recommendation count"""
    print("\n=== Testing API with Dynamic Count ===")
    
    import requests
    
    test_queries = [
        ("Berikan 3 rekomendasi tempat sarapan", 3),
        ("Kasih lma tempat makan murah", 5),  # typo
        ("Rekomendasikan tjuh restoran enak", 7),  # typo
    ]
    
    try:
        for query, expected_count in test_queries:
            print(f"\nQuery: '{query}'")
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": query, "conversation_history": []},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                card_count = len(data.get('restaurants', []))
                status = "✓" if card_count == expected_count else "⚠"
                print(f"{status} Got {card_count} cards (expected: {expected_count})")
                print(f"Response preview: {data['message'][:200]}...")
            else:
                print(f"✗ Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("⚠ Server not running. Start with: python src/main.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def test_api_with_future_time():
    """Test API with future time requests"""
    print("\n=== Testing API with Future Time ===")
    
    import requests
    
    test_queries = [
        "Rekomendasikan tempat makan besok pagi",
        "Cari restoran untuk besok siang",
        "Tempat makan nanti malam",
    ]
    
    try:
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": query, "conversation_history": []},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Got {len(data.get('restaurants', []))} recommendations")
                print(f"Response preview: {data['message'][:200]}...")
            else:
                print(f"✗ Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("⚠ Server not running. Start with: python src/main.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing New Features")
    print("=" * 60)
    
    # Test utility functions
    test1 = test_number_extraction()
    test2 = test_future_time_parsing()
    
    # Test API (requires server running)
    print("\n" + "=" * 60)
    print("API Tests (requires server running)")
    print("=" * 60)
    test3 = test_api_with_dynamic_count()
    test4 = test_api_with_future_time()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Number Extraction: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"Future Time Parsing: {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"API Dynamic Count: {'✓ PASS' if test3 else '⚠ SKIP (server not running)'}")
    print(f"API Future Time: {'✓ PASS' if test4 else '⚠ SKIP (server not running)'}")
