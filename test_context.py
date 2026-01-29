#!/usr/bin/env python3
"""
Quick test to verify context extraction works
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ldr_client import LdrClient

def test_context():
    """Test basic context extraction"""
    print("Testing context extraction...")
    
    with LdrClient(auto_start_server=True) as client:
        # Test with ActivityStreams (small, fast)
        url = "https://www.w3.org/ns/activitystreams"
        print(f"\nFetching context from: {url}")
        
        context = client.context(url, depth=2)
        
        print(f"✓ Got context: {context}")
        print(f"✓ Type: {type(context)}")
        
        # Test cache
        context2 = client.context(url, depth=2)
        stats = client.cache_stats()
        print(f"✓ Cache has {stats['size']} entries")
        
        print("\n✅ All tests passed!")
        return True

if __name__ == "__main__":
    try:
        test_context()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
