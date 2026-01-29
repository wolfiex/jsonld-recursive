#!/usr/bin/env python3
"""Test the new context() method."""

from lib.ldr_client import LdrClient
import json

# Test with a simple context URL
with LdrClient(auto_start_server=True) as client:
    print("Testing context extraction...\n")
    
    # Test 1: Get context from a URL
    print("=" * 60)
    print("Test 1: Get compiled context from schema.org")
    print("=" * 60)
    try:
        context = client.context("https://schema.org/", depth=1)
        print("\nCompiled context:")
        print(json.dumps(context, indent=2)[:500] + "...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test 2: Cache stats")
    print("=" * 60)
    stats = client.cache_stats()
    print(f"Cache size: {stats['size']}")
    print(f"Cached keys: {stats['keys']}")
