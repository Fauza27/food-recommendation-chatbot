"""
Run all tests untuk verify setup
"""
import sys

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def main():
    print_header("Food Recommendation Chatbot - Setup Verification")
    
    all_passed = True
    
    # Test 1: Config
    print_header("Test 1: Configuration")
    try:
        from config import get_settings
        settings = get_settings()
        print("✓ Configuration loaded successfully")
        print(f"  - AWS Region: {settings.aws_region}")
        print(f"  - Qdrant URL: {settings.qdrant_url[:30]}...")
        print(f"  - Collection: {settings.qdrant_collection_name}")
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        all_passed = False
    
    # Test 2: AWS Connection
    print_header("Test 2: AWS Bedrock Connection")
    try:
        from test_aws import test_aws_connection
        if not test_aws_connection():
            all_passed = False
    except Exception as e:
        print(f"✗ AWS test failed: {e}")
        all_passed = False
    
    # Test 3: Qdrant Connection
    print_header("Test 3: Qdrant Connection")
    try:
        from test_qdrant import test_qdrant_connection
        if not test_qdrant_connection():
            all_passed = False
    except Exception as e:
        print(f"✗ Qdrant test failed: {e}")
        all_passed = False
    
    # Test 4: Dependencies
    print_header("Test 4: Python Dependencies")
    required_packages = [
        'fastapi',
        'uvicorn',
        'langchain',
        'langchain_aws',
        'qdrant_client',
        'pandas',
        'boto3',
        'pydantic',
        'pytz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing_packages.append(package)
            all_passed = False
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
    
    # Test 5: Data File
    print_header("Test 5: Data File")
    try:
        import os
        if os.path.exists('cleaned_enhanced_data_2.csv'):
            import pandas as pd
            df = pd.read_csv('cleaned_enhanced_data_2.csv')
            print(f"✓ Data file found")
            print(f"  - Records: {len(df)}")
            print(f"  - Columns: {len(df.columns)}")
        else:
            print("✗ Data file 'cleaned_enhanced_data_2.csv' not found")
            all_passed = False
    except Exception as e:
        print(f"✗ Data file test failed: {e}")
        all_passed = False
    
    # Summary
    print_header("Test Summary")
    if all_passed:
        print("✓ All tests passed!")
        print("\nNext steps:")
        print("1. Run: python ingest_data.py (if not done yet)")
        print("2. Run: python main.py")
        print("3. Open: http://localhost:8000/docs")
    else:
        print("✗ Some tests failed")
        print("\nPlease fix the issues above before proceeding")
        print("Check QUICKSTART.md for troubleshooting guide")
        sys.exit(1)

if __name__ == "__main__":
    main()
