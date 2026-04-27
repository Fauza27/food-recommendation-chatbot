"""
Test script for Posts API endpoints
"""
import requests
import json

# Base URL - adjust if needed
BASE_URL = "http://localhost:8000"

def test_get_posts_basic():
    """Test basic posts retrieval"""
    print("\n=== Test 1: Get Posts (Basic) ===")
    response = requests.get(f"{BASE_URL}/api/posts")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total posts: {data['total']}")
        print(f"Page: {data['page']}")
        print(f"Limit: {data['limit']}")
        print(f"Total pages: {data['total_pages']}")
        print(f"Posts returned: {len(data['posts'])}")
        
        if data['posts']:
            print("\nFirst post:")
            print(json.dumps(data['posts'][0], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")

def test_get_posts_pagination():
    """Test pagination"""
    print("\n=== Test 2: Get Posts (Pagination) ===")
    response = requests.get(f"{BASE_URL}/api/posts?page=2&limit=10")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Page: {data['page']}")
        print(f"Limit: {data['limit']}")
        print(f"Posts returned: {len(data['posts'])}")
    else:
        print(f"Error: {response.text}")

def test_search_posts():
    """Test search functionality"""
    print("\n=== Test 3: Search Posts ===")
    
    # Test search by nama_tempat
    search_queries = ["japanese", "ayam", "mcd"]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        response = requests.get(f"{BASE_URL}/api/posts?search={query}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} results")
            if data['posts']:
                print(f"First result: {data['posts'][0]['nama_tempat']}")
        else:
            print(f"Error: {response.text}")

def test_filter_by_category():
    """Test category filtering"""
    print("\n=== Test 4: Filter by Category ===")
    
    categories = ["Japanese Food", "Fast Food", "warung_tenda"]
    
    for category in categories:
        print(f"\nFiltering by: '{category}'")
        response = requests.get(f"{BASE_URL}/api/posts?category={category}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} results")
            if data['posts']:
                print(f"First result: {data['posts'][0]['nama_tempat']} - {data['posts'][0]['kategori_makanan']}")
        else:
            print(f"Error: {response.text}")

def test_search_and_filter():
    """Test combined search and filter"""
    print("\n=== Test 5: Search + Filter ===")
    response = requests.get(f"{BASE_URL}/api/posts?search=ayam&category=pedas")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} results with search='ayam' and category='pedas'")
        if data['posts']:
            for i, post in enumerate(data['posts'][:3], 1):
                print(f"\n{i}. {post['nama_tempat']}")
                print(f"   Kategori: {post['kategori_makanan']}")
                print(f"   Tags: {', '.join(post['tags'][:5])}")
    else:
        print(f"Error: {response.text}")

def test_get_categories():
    """Test get all categories"""
    print("\n=== Test 6: Get Categories ===")
    response = requests.get(f"{BASE_URL}/api/categories")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total categories: {data['total']}")
        print(f"Categories: {', '.join(data['categories'][:20])}")
        if len(data['categories']) > 20:
            print(f"... and {len(data['categories']) - 20} more")
    else:
        print(f"Error: {response.text}")

def test_edge_cases():
    """Test edge cases"""
    print("\n=== Test 7: Edge Cases ===")
    
    # Invalid page
    print("\nTest invalid page (page=0):")
    response = requests.get(f"{BASE_URL}/api/posts?page=0")
    print(f"Status Code: {response.status_code} (should be 400)")
    
    # Invalid limit
    print("\nTest invalid limit (limit=200):")
    response = requests.get(f"{BASE_URL}/api/posts?limit=200")
    print(f"Status Code: {response.status_code} (should be 400)")
    
    # Empty search
    print("\nTest empty search:")
    response = requests.get(f"{BASE_URL}/api/posts?search=xyzabc123notfound")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} results (should be 0 or very few)")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Posts API Endpoints")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the backend server is running!")
    print("Run: cd backend/src && python main.py")
    print("=" * 60)
    
    try:
        # Run all tests
        test_get_posts_basic()
        test_get_posts_pagination()
        test_search_posts()
        test_filter_by_category()
        test_search_and_filter()
        test_get_categories()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the backend is running on", BASE_URL)
    except Exception as e:
        print(f"\n❌ Error: {e}")
