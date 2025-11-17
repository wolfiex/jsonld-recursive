#!/usr/bin/env python3
"""
Example: Using jsonld-recursive Python Client
"""

from ldr_client import LdrClient

# Example 1: Basic usage with auto-start server
print("Example 1: Auto-start server")
print("-" * 50)

with LdrClient(auto_start_server=True) as client:
    result = client.compact(
        "https://wcrp-cmip.github.io/CMIP7-CVs/experiment/graph.jsonld",
        depth=3
    )
    print(f"Compacted {len(result)} items")


# Example 2: Using URL mappings for local files
print("\nExample 2: URL mappings for local files")
print("-" * 50)

with LdrClient(auto_start_server=True) as client:
    # Set up chained mappings
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local-cvs/${rest}"
    })
    
    # Now this will chain through mappings and load from local file
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    print(f"Result: {type(result)}")


# Example 3: Batch processing
print("\nExample 3: Batch processing")
print("-" * 50)

urls = [
    "https://example.com/doc1.jsonld",
    "https://example.com/doc2.jsonld",
    "https://example.com/doc3.jsonld"
]

with LdrClient(auto_start_server=True) as client:
    # Process multiple URLs
    for url in urls:
        try:
            result = client.compact(url, depth=2)
            print(f"✓ Processed: {url}")
        except Exception as e:
            print(f"✗ Failed: {url} - {e}")


# Example 4: Expand instead of compact
print("\nExample 4: Expand operation")
print("-" * 50)

with LdrClient(auto_start_server=True) as client:
    expanded = client.expand(
        "https://wcrp-cmip.github.io/CMIP7-CVs/experiment/graph.jsonld",
        depth=2
    )
    print(f"Expanded result type: {type(expanded)}")


# Example 5: Runtime mapping updates
print("\nExample 5: Runtime mapping updates")
print("-" * 50)

with LdrClient(auto_start_server=True) as client:
    # Set initial mappings
    client.set_mappings({
        "test:*": "https://test.example.com/${rest}"
    })
    
    # Get current mappings
    current = client.get_mappings()
    print(f"Current mappings: {current}")
    
    # Update mappings
    client.set_mappings({
        "test:*": "https://test.example.com/${rest}",
        "local:*": "/home/user/data/${rest}"
    })
    
    # Clear when done
    client.clear_mappings()
    print("Mappings cleared")


# Example 6: Manual server control
print("\nExample 6: Manual server control")
print("-" * 50)

# Connect to existing server (no auto-start)
client = LdrClient(base_url="http://localhost:3000")

# Check if server is running
if client._is_server_running():
    print("Server is running")
    result = client.compact("https://example.com/data.jsonld", depth=2)
else:
    print("Server is not running - start it with: node ldr-server.js")

# Clean up
client.close()


# Example 7: Custom timeout and retries
print("\nExample 7: Custom configuration")
print("-" * 50)

with LdrClient(
    base_url="http://localhost:3000",
    timeout=60,  # 60 second timeout
    max_retries=5,  # Retry up to 5 times
    auto_start_server=True
) as client:
    result = client.compact(
        "https://wcrp-cmip.github.io/CMIP7-CVs/experiment/graph.jsonld",
        depth=3
    )
    print("Processed with custom config")
