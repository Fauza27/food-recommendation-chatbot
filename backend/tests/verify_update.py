"""
Verify v1.1.0 update - Check all changes are in place
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_function_in_file(filepath, function_name):
    """Check if function exists in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            exists = function_name in content
            status = "✓" if exists else "✗"
            print(f"  {status} Function '{function_name}' in {filepath}")
            return exists
    except:
        print(f"  ✗ Could not read {filepath}")
        return False

def main():
    print("="*70)
    print("VERIFYING v1.1.0 UPDATE")
    print("="*70)
    
    all_checks = []
    
    # Check new files
    print("\n1. NEW FILES")
    print("-"*70)
    all_checks.append(check_file_exists("docs/NEW_FEATURES.md", "New features documentation"))
    all_checks.append(check_file_exists("tests/test_new_features.py", "New features tests"))
    all_checks.append(check_file_exists("tests/test_manual_examples.py", "Manual test examples"))
    all_checks.append(check_file_exists("FEATURE_UPDATE_v1.1.0.md", "Feature update summary"))
    all_checks.append(check_file_exists("QUICK_UPDATE_SUMMARY.md", "Quick update summary"))
    
    # Check modified files
    print("\n2. MODIFIED FILES")
    print("-"*70)
    all_checks.append(check_file_exists("src/utils.py", "Utils module"))
    all_checks.append(check_file_exists("src/rag_service.py", "RAG service"))
    all_checks.append(check_file_exists("README.md", "README"))
    all_checks.append(check_file_exists("START_HERE.md", "Start here guide"))
    all_checks.append(check_file_exists("docs/CHANGELOG.md", "Changelog"))
    
    # Check new functions in utils.py
    print("\n3. NEW FUNCTIONS IN utils.py")
    print("-"*70)
    all_checks.append(check_function_in_file("src/utils.py", "extract_number_from_text"))
    all_checks.append(check_function_in_file("src/utils.py", "parse_future_time"))
    all_checks.append(check_function_in_file("src/utils.py", "check_operational_status_at_time"))
    
    # Check imports in rag_service.py
    print("\n4. UPDATED IMPORTS IN rag_service.py")
    print("-"*70)
    all_checks.append(check_function_in_file("src/rag_service.py", "extract_number_from_text"))
    all_checks.append(check_function_in_file("src/rag_service.py", "parse_future_time"))
    all_checks.append(check_function_in_file("src/rag_service.py", "check_operational_status_at_time"))
    
    # Check updated logic in rag_service.py
    print("\n5. UPDATED LOGIC IN rag_service.py")
    print("-"*70)
    all_checks.append(check_function_in_file("src/rag_service.py", "requested_count = extract_number_from_text"))
    all_checks.append(check_function_in_file("src/rag_service.py", "future_time_info = parse_future_time"))
    all_checks.append(check_function_in_file("src/rag_service.py", "max_cards=requested_count"))
    
    # Check documentation updates
    print("\n6. DOCUMENTATION UPDATES")
    print("-"*70)
    all_checks.append(check_function_in_file("README.md", "Dynamic Count"))
    all_checks.append(check_function_in_file("README.md", "Typo Tolerance"))
    all_checks.append(check_function_in_file("README.md", "Future Time"))
    all_checks.append(check_function_in_file("START_HERE.md", "NEW_FEATURES.md"))
    all_checks.append(check_function_in_file("docs/CHANGELOG.md", "1.1.0-free"))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n✅ ALL CHECKS PASSED!")
        print("v1.1.0 update is complete and ready to use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} checks failed!")
        print("Please review the failed checks above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
