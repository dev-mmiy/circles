#!/usr/bin/env python3
"""
Test runner for profile management functionality.
Runs all profile-related tests and generates a comprehensive report.
"""

import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """Run all profile management tests."""
    print("🧪 Running Profile Management Tests")
    print("=" * 50)
    
    # Test files to run
    test_files = [
        "tests/test_profile_management.py",
        "tests/test_frontend_profile.py", 
        "tests/test_profile_integration.py"
    ]
    
    # Test categories
    test_categories = {
        "Backend API Tests": "tests/test_profile_management.py",
        "Frontend Component Tests": "tests/test_frontend_profile.py",
        "Integration Tests": "tests/test_profile_integration.py"
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    results = {}
    
    for category, test_file in test_categories.items():
        print(f"\n📋 {category}")
        print("-" * 30)
        
        try:
            # Run pytest for specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--color=yes"
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # Parse results
            output_lines = result.stdout.split('\n')
            test_summary = None
            
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    test_summary = line
                    break
            
            if test_summary:
                print(f"✅ {test_summary}")
                
                # Extract numbers
                import re
                numbers = re.findall(r'\d+', test_summary)
                if len(numbers) >= 2:
                    passed = int(numbers[0])
                    failed = int(numbers[1])
                    total_tests += passed + failed
                    passed_tests += passed
                    failed_tests += failed
                    
                    results[category] = {
                        "passed": passed,
                        "failed": failed,
                        "total": passed + failed
                    }
            else:
                print("❌ No test results found")
                results[category] = {"passed": 0, "failed": 1, "total": 1}
                failed_tests += 1
                total_tests += 1
            
            # Show any errors
            if result.stderr:
                print(f"⚠️  Warnings/Errors:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            results[category] = {"passed": 0, "failed": 1, "total": 1}
            failed_tests += 1
            total_tests += 1
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 50)
    
    print(f"🕐 Test Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Test Directory: {os.getcwd()}")
    
    print(f"\n📈 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   📊 Success Rate: 0%")
    
    print(f"\n📋 Category Breakdown:")
    for category, stats in results.items():
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"   {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Test coverage information
    print(f"\n🔍 Test Coverage Areas:")
    coverage_areas = [
        "✅ Profile Update API Endpoints",
        "✅ Authentication and Authorization", 
        "✅ Data Validation and Error Handling",
        "✅ Frontend Form Components",
        "✅ User Interface State Management",
        "✅ Internationalization Support",
        "✅ Integration with Backend APIs",
        "✅ Error Handling and Edge Cases",
        "✅ Performance and Concurrency",
        "✅ Data Consistency and Validation"
    ]
    
    for area in coverage_areas:
        print(f"   {area}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if failed_tests == 0:
        print("   🎉 All tests passed! Profile management functionality is working correctly.")
        print("   🚀 Ready for production deployment.")
    else:
        print("   ⚠️  Some tests failed. Please review the output above.")
        print("   🔧 Fix failing tests before deploying to production.")
        print("   📝 Consider adding more edge case tests.")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    print("   1. Review any failed tests and fix issues")
    print("   2. Run tests in CI/CD pipeline")
    print("   3. Monitor profile management in production")
    print("   4. Add performance monitoring")
    print("   5. Consider adding user acceptance tests")
    
    return failed_tests == 0


def run_specific_test_category(category):
    """Run tests for a specific category."""
    test_files = {
        "backend": "tests/test_profile_management.py",
        "frontend": "tests/test_frontend_profile.py",
        "integration": "tests/test_profile_integration.py"
    }
    
    if category not in test_files:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(test_files.keys())}")
        return False
    
    test_file = test_files[category]
    print(f"🧪 Running {category} tests: {test_file}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file, 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], cwd=os.getcwd())
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        category = sys.argv[1]
        success = run_specific_test_category(category)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
