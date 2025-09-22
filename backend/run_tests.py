#!/usr/bin/env python3
"""Test runner script for WSJF backend."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner."""
    os.chdir(Path(__file__).parent)

    print("🧪 WSJF Backend Test Runner")
    print("=" * 50)

    # Test categories to run
    test_categories = [
        (["pytest", "-m", "unit", "-v"], "Unit Tests"),
        (["pytest", "-m", "database", "-v"], "Database Tests"),
        (["pytest", "-m", "integration", "-v"], "Integration Tests"),
    ]

    # Optional: Run all tests with coverage
    if "--coverage" in sys.argv:
        test_categories.append(
            (
                [
                    "pytest",
                    "--cov=app",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                ],
                "All Tests with Coverage",
            )
        )

    # Optional: Run only specific category
    if "--unit" in sys.argv:
        test_categories = [(["pytest", "-m", "unit", "-v"], "Unit Tests Only")]
    elif "--database" in sys.argv:
        test_categories = [(["pytest", "-m", "database", "-v"], "Database Tests Only")]
    elif "--integration" in sys.argv:
        test_categories = [
            (["pytest", "-m", "integration", "-v"], "Integration Tests Only")
        ]

    success_count = 0
    total_count = len(test_categories)

    for cmd, description in test_categories:
        if run_command(cmd, description):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_count} categories passed")

    if success_count == total_count:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
