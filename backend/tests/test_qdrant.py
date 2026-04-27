"""
Script untuk test koneksi Qdrant
"""
from qdrant_client import QdrantClient
from config import get_settings

def test_qdrant_connection():
    """Test Qdrant connection"""
    print("Testing Qdrant connection...")
    
    settings = get_settings()
    
    try:
        # Create Qdrant client
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        
        print("✓ Qdrant client created successfully")
        print(f"  URL: {settings.qdrant_url}")
        print(f"  API Key: {settings.qdrant_api_key[:10]}***")
        
        # Get collections
        print("\nFetching collections...")
        collections = client.get_collections()
        
        print(f"✓ Found {len(collections.collections)} collection(s)")
        
        for collection in collections.collections:
            print(f"\n  Collection: {collection.name}")
            
            # Get collection info
            try:
                info = client.get_collection(collection.name)
                print(f"    Points: {info.points_count}")
                
                # Handle different vector config formats
                if hasattr(info.config.params.vectors, 'size'):
                    print(f"    Vector size: {info.config.params.vectors.size}")
                    print(f"    Distance: {info.config.params.vectors.distance}")
                else:
                    print(f"    Vector config: Multiple vectors")
            except Exception as e:
                print(f"    Error getting details: {e}")
        
        # Check if our collection exists
        collection_names = [c.name for c in collections.collections]
        if settings.qdrant_collection_name in collection_names:
            print(f"\n✓ Collection '{settings.qdrant_collection_name}' exists")
            
            # Get detailed info
            info = client.get_collection(settings.qdrant_collection_name)
            print(f"  Points count: {info.points_count}")
            
            if info.points_count == 0:
                print("  ⚠ Collection is empty - run 'python ingest_data.py' to populate")
            elif info.points_count < 3900:
                print(f"  ⚠ Collection has {info.points_count} points (expected ~3900)")
            else:
                print("  ✓ Collection is properly populated")
        else:
            print(f"\n✗ Collection '{settings.qdrant_collection_name}' not found")
            print("  Run 'python ingest_data.py' to create and populate the collection")
        
        print("\n✓ Qdrant connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Qdrant connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct Qdrant credentials")
        print("2. Verify QDRANT_URL and QDRANT_API_KEY")
        print("3. Ensure your Qdrant cluster is running")
        print("4. Check if you can access the URL in browser")
        return False

if __name__ == "__main__":
    test_qdrant_connection()
