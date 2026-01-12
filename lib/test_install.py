#!/usr/bin/env python3
"""
Installation verification tests for jsonld-recursive.

Run with:
    python -c "from jsonld_recursive import test; test()"
    
Or:
    python -m jsonld_recursive.test_install
    
Or after install:
    jsonld-recursive-test
"""

import os
import sys
import json
import time
from pathlib import Path


def get_test_data_dir() -> Path:
    """Get the path to the bundled test data directory."""
    return Path(__file__).parent / "testdata"


def test_local_files() -> bool:
    """
    Test that local JSON-LD files can be loaded without a server.
    This tests the basic file structure is intact.
    
    This is the CORE test that runs during installation.
    """
    print("Testing local file loading...", flush=True)
    
    test_dir = get_test_data_dir()
    
    if not test_dir.exists():
        print(f"  ✗ Test data directory not found: {test_dir}")
        return False
    
    # Check all required files exist
    required_files = ["main.jsonld", "linked.jsonld", "context.jsonld"]
    
    for filename in required_files:
        filepath = test_dir / filename
        if not filepath.exists():
            print(f"  ✗ Missing test file: {filename}")
            return False
        
        # Verify it's valid JSON
        try:
            with open(filepath) as f:
                data = json.load(f)
            print(f"  ✓ {filename} - valid JSON")
        except json.JSONDecodeError as e:
            print(f"  ✗ {filename} - invalid JSON: {e}")
            return False
    
    # Check that main.jsonld references linked.jsonld correctly
    main_path = test_dir / "main.jsonld"
    with open(main_path) as f:
        main_data = json.load(f)
    
    if "related" not in main_data:
        print("  ✗ main.jsonld missing 'related' field")
        return False
    
    if main_data["related"] != "./linked.jsonld":
        print("  ✗ main.jsonld 'related' field should reference ./linked.jsonld")
        return False
    
    # Check context reference
    if main_data.get("@context") != "./context.jsonld":
        print("  ✗ main.jsonld '@context' should reference ./context.jsonld")
        return False
    
    # Verify the client module can be imported
    try:
        from . import LdrClient
        print("  ✓ LdrClient imports successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import LdrClient: {e}")
        return False
    
    print("  ✓ All test files valid and properly linked")
    return True


def test_server_connection(base_url: str = "http://localhost:3000", timeout: int = 2) -> bool:
    """
    Test connection to an existing LDR server.
    Returns True if server is running and healthy.
    """
    print(f"Testing server connection at {base_url}...", flush=True)
    
    try:
        import requests
        response = requests.get(f"{base_url}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Server healthy - cache: {data.get('cache_size', 0)}, mappings: {data.get('mappings_count', 0)}")
            return True
        else:
            print(f"  ✗ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Could not connect: {e}")
        return False


def test_client_with_local_files(auto_start: bool = False) -> bool:
    """
    Test the LdrClient with bundled test files.
    This tests the FULL pipeline: server start, expand, compact with local files.
    
    Requirements:
    - Node.js installed
    - jsonld npm package installed (npm install -g jsonld)
    
    Args:
        auto_start: If True, attempt to auto-start the server
    """
    print("Testing LdrClient with local files...", flush=True)
    
    # Check prerequisites
    import shutil
    if not shutil.which('node'):
        print("  ✗ Node.js not found - required for server")
        print("    Install from: https://nodejs.org/")
        return False
    print("  ✓ Node.js found")
    
    from .ldr_client import LdrClient
    
    test_dir = get_test_data_dir()
    main_file = test_dir / "main.jsonld"
    main_file_abs = str(main_file.absolute())
    
    client = None
    try:
        client = LdrClient(auto_start_server=auto_start, timeout=30)
        
        # Check server is running
        if not client._is_server_running():
            if auto_start:
                print("  ✗ Failed to auto-start server")
                print("    Make sure Node.js is installed and 'ldr' command is available")
                print("    Or install globally: npm install -g jsonld-recursive")
                return False
            else:
                print("  ✗ Server not running (use auto_start=True or start manually)")
                return False
        
        print("  ✓ Server is running")
        
        # Clear any existing cache
        try:
            client.cache_clear()
        except:
            pass
        
        # Test expand with the local file
        print(f"  Testing expand on: {main_file_abs}")
        try:
            result = client.expand(main_file_abs, depth=2, verbose=False)
            
            if result is None:
                print("  ✗ Expand returned None")
                return False
            
            # Check we got expanded JSON-LD (should be a list or dict)
            if isinstance(result, list):
                print(f"  ✓ Expand succeeded - got list with {len(result)} items")
            elif isinstance(result, dict):
                print(f"  ✓ Expand succeeded - got dict with keys: {list(result.keys())[:5]}...")
            else:
                print(f"  ✓ Expand succeeded - got {type(result).__name__}")
                
        except Exception as e:
            print(f"  ✗ Expand failed: {e}")
            return False
        
        # Test compact with the local file
        print(f"  Testing compact on: {main_file_abs}")
        try:
            result = client.compact(main_file_abs, depth=2, verbose=False)
            
            if result is None:
                print("  ✗ Compact returned None")
                return False
            
            if isinstance(result, dict):
                # Check if we got the expected fields back
                has_context = "@context" in result
                has_id = "@id" in result
                print(f"  ✓ Compact succeeded - has @context: {has_context}, has @id: {has_id}")
            else:
                print(f"  ✓ Compact succeeded - got {type(result).__name__}")
                
        except Exception as e:
            print(f"  ✗ Compact failed: {e}")
            return False
        
        # Check cache is working
        try:
            stats = client.cache_stats()
            cache_size = stats.get('size', 0)
            print(f"  ✓ Cache working - {cache_size} entries cached")
        except Exception as e:
            print(f"  ⚠ Cache check failed (non-fatal): {e}")
        
        print("  ✓ All server tests passed")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up: stop server if we auto-started it
        if client:
            try:
                if client.auto_started:
                    print("  Stopping auto-started server...")
                    client.stop_server()
                client.close()
            except:
                pass


def test(auto_start_server: bool = False, verbose: bool = True) -> bool:
    """
    Run all installation verification tests.
    
    Args:
        auto_start_server: If True, attempt to auto-start the server for integration tests
        verbose: Print detailed output
        
    Returns:
        True if all tests pass, False otherwise
    """
    print("=" * 60)
    print("jsonld-recursive Installation Verification")
    print("=" * 60)
    print()
    
    results = {}
    
    # Test 1: Local files exist and are valid (REQUIRED)
    results["local_files"] = test_local_files()
    print()
    
    # Test 2: Server connection check
    results["server_connection"] = test_server_connection()
    print()
    
    # Test 3: Full integration test with server
    if results["server_connection"] or auto_start_server:
        results["server_with_local_files"] = test_client_with_local_files(auto_start=auto_start_server)
    else:
        print("Skipping server integration test (no server, use --auto-start)")
        results["server_with_local_files"] = None
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_required_passed = True
    for name, passed in results.items():
        if passed is None:
            status = "SKIPPED"
        elif passed:
            status = "PASSED"
        else:
            status = "FAILED"
            all_required_passed = False
        print(f"  {name}: {status}")
    
    print()
    if all_required_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    return all_required_passed


def main():
    """CLI entry point for running tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test jsonld-recursive installation")
    parser.add_argument(
        "--auto-start", "-a",
        action="store_true",
        help="Auto-start the server for integration tests"
    )
    parser.add_argument(
        "--server-only", "-s",
        action="store_true", 
        help="Only test server connection"
    )
    parser.add_argument(
        "--basic", "-b",
        action="store_true",
        help="Only run basic file tests (no server required)"
    )
    
    args = parser.parse_args()
    
    if args.server_only:
        success = test_server_connection()
    elif args.basic:
        success = test_local_files()
    else:
        success = test(auto_start_server=args.auto_start)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
