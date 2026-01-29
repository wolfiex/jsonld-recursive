#!/usr/bin/env python3
"""
Example: Get compiled context from JSON-LD URLs

This script demonstrates how to extract and save compiled contexts
from JSON-LD documents using jsonld-recursive.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import ldr_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ldr_client import LdrClient


def get_context_simple(url, depth=3):
    """
    Simplest way to get a compiled context.
    Server starts and stops automatically.
    """
    print(f"Getting context from: {url}")
    print(f"Recursion depth: {depth}\n")
    
    with LdrClient(auto_start_server=True) as client:
        context = client.context(url, depth=depth)
        return context


def get_context_with_mappings(url, mappings, depth=3):
    """
    Get context with URL mappings for local development.
    """
    print(f"Getting context from: {url}")
    print(f"Using mappings: {json.dumps(mappings, indent=2)}")
    print(f"Recursion depth: {depth}\n")
    
    with LdrClient(auto_start_server=True) as client:
        # Set up mappings
        client.set_mappings(mappings)
        
        # Get context
        context = client.context(url, depth=depth)
        return context


def get_multiple_contexts(urls, depth=3):
    """
    Get contexts from multiple URLs efficiently.
    Reuses server connection and caching.
    """
    print(f"Getting contexts from {len(urls)} URLs")
    print(f"Recursion depth: {depth}\n")
    
    contexts = {}
    
    with LdrClient(auto_start_server=True) as client:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            try:
                contexts[url] = client.context(url, depth=depth)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                contexts[url] = None
        
        # Show cache stats
        stats = client.cache_stats()
        print(f"\nCache: {stats['size']} entries")
    
    return contexts


def save_context(context, output_path):
    """Save context to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(context, f, indent=2)
    
    print(f"\n✓ Saved to: {output_path}")


# Example 1: Simple usage
def example1():
    """Get context from schema.org"""
    print("="*60)
    print("Example 1: Simple context extraction")
    print("="*60 + "\n")
    
    context = get_context_simple("https://schema.org/", depth=2)
    
    print("\nExtracted context keys:", list(context.keys())[:10])
    print(f"Total terms: {len(context)}")
    
    # Save it
    save_context(context, "output/schema-org-context.json")


# Example 2: With URL mappings
def example2():
    """Get context using URL mappings for local files"""
    print("\n" + "="*60)
    print("Example 2: Context with URL mappings")
    print("="*60 + "\n")
    
    mappings = {
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/Users/daniel.ellis/local-cvs/${rest}"
    }
    
    try:
        context = get_context_with_mappings(
            "cmip7:experiment/context.jsonld",
            mappings,
            depth=3
        )
        
        print("\nExtracted context keys:", list(context.keys())[:10])
        save_context(context, "output/cmip7-context.json")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("(This is expected if local files don't exist)")


# Example 3: Batch processing
def example3():
    """Get contexts from multiple URLs"""
    print("\n" + "="*60)
    print("Example 3: Batch context extraction")
    print("="*60 + "\n")
    
    urls = [
        "https://schema.org/",
        "https://www.w3.org/ns/activitystreams",
    ]
    
    contexts = get_multiple_contexts(urls, depth=2)
    
    # Save each context
    for url, context in contexts.items():
        if context:
            # Create filename from URL
            filename = url.replace("https://", "").replace("/", "-")
            if filename.endswith("-"):
                filename = filename[:-1]
            filename = f"output/{filename}-context.json"
            
            save_context(context, filename)


# Example 4: Compare contexts
def example4():
    """Compare contexts from different sources"""
    print("\n" + "="*60)
    print("Example 4: Context comparison")
    print("="*60 + "\n")
    
    with LdrClient(auto_start_server=True) as client:
        # Get two related contexts
        context1 = client.context("https://schema.org/", depth=1)
        context2 = client.context("https://schema.org/", depth=2)
        
        # Compare
        keys1 = set(context1.keys()) if isinstance(context1, dict) else set()
        keys2 = set(context2.keys()) if isinstance(context2, dict) else set()
        
        print(f"Depth 1: {len(keys1)} terms")
        print(f"Depth 2: {len(keys2)} terms")
        print(f"Additional terms at depth 2: {len(keys2 - keys1)}")
        
        if keys2 - keys1:
            print(f"\nNew terms: {list(keys2 - keys1)[:5]}...")


if __name__ == "__main__":
    # Run all examples
    try:
        example1()
        example2()
        example3()
        example4()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
