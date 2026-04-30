#!/usr/bin/env python3
# review: reference-asset
# review: allow-human-readable-output
# Bisection script to find which test creates unwanted files/state
# Usage: python find_polluter.py <file_or_dir_to_check> <test_pattern>
# Example: python find_polluter.py ".git" "src/**/*.test.ts"
# This helper is intended for interactive debugging. Human-readable terminal
# output is intentional; it is not a machine-consumed interface.

import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Find which test creates unwanted files/state")
    parser.add_argument("pollution_check", help="File or directory to check")
    parser.add_argument("test_pattern", help="Glob pattern for test files (e.g., 'src/**/*.test.ts')")
    args = parser.parse_args()

    pollution_check = Path(args.pollution_check)
    
    print(f"🔍 Searching for test that creates: {pollution_check}")
    print(f"Test pattern: {args.test_pattern}\n")
    
    test_files = sorted(list(Path(".").glob(args.test_pattern)))
    total = len(test_files)
    print(f"Found {total} test files\n")

    for count, test_file in enumerate(test_files, start=1):
        if pollution_check.exists():
            print(f"⚠️  Pollution already exists before test {count}/{total}")
            print(f"   Skipping: {test_file}")
            continue

        print(f"[{count}/{total}] Testing: {test_file}")
        
        # 兼容跨平台的测试执行 (Windows 下建议使用 shell=True 调用 npm)
        subprocess.run(f"npm test {test_file}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if pollution_check.exists():
            print("\n🎯 FOUND POLLUTER!")
            print(f"   Test: {test_file}")
            print(f"   Created: {pollution_check}\n")
            print("Pollution details:")
            if sys.platform == "win32":
                subprocess.run(f"dir {pollution_check}", shell=True)
            else:
                subprocess.run(f"ls -la {pollution_check}", shell=True)
            print("\nTo investigate:")
            print(f"  npm test {test_file}    # Run just this test")
            sys.exit(1)

    print("\n✅ No polluter found - all tests clean!")
    sys.exit(0)

if __name__ == "__main__":
    main()
