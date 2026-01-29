# Getting Compiled Contexts - Quick Reference

## Overview

`jsonld-recursive` can extract and compile JSON-LD `@context` definitions from URLs or local files, recursively resolving nested context references.

## Python API

### Basic Usage

```python
from lib.ldr_client import LdrClient

# Get compiled context
with LdrClient(auto_start_server=True) as client:
    context = client.context("https://schema.org/", depth=3)
    print(context)
```

### Save to File

```python
import json
with LdrClient(auto_start_server=True) as client:
    context = client.context("https://schema.org/", depth=3)
    
    with open('context.json', 'w') as f:
        json.dump(context, f, indent=2)
```

### With URL Mappings

```python
with LdrClient(auto_start_server=True) as client:
    # Map remote URLs to local files
    client.set_mappings({
        "https://example.com/*": "/local/path/${rest}"
    })
    
    context = client.context("https://example.com/context.jsonld", depth=3)
```

### Batch Processing

```python
with LdrClient(auto_start_server=True) as client:
    urls = [
        "https://schema.org/",
        "https://www.w3.org/ns/activitystreams",
    ]
    
    for url in urls:
        context = client.context(url, depth=3)
        # Process context...
```

## CLI

### Basic Commands

```bash
# Standalone (no caching)
ldr context https://schema.org/ -d 3

# With server (enables caching)
ldr server start
ldr context https://schema.org/ -d 3 --server
ldr server stop

# Save to file
ldr context https://schema.org/ -d 3 > context.json

# Local file
ldr context /path/to/file.jsonld -d 2
```

### With Mappings

```bash
# Start server with mappings
ldr server start 3333

# Set mappings
ldr mappings set '{"prefix:*":"https://example.com/${rest}"}'

# Get context using mapped URL
ldr context prefix:data/context.jsonld -d 3 --server

# Clear mappings
ldr mappings clear
```

## HTTP API

```bash
# Start server
ldr server start

# POST to /context endpoint
curl -X POST http://localhost:3333/context \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://schema.org/",
    "depth": 3
  }' | jq '.result'
```

## Parameters

- **url**: URL or file path to JSON-LD document with @context
- **depth**: Recursion depth for nested contexts (default: 2)
  - depth=1: Only the immediate context
  - depth=2: Resolves one level of nested contexts
  - depth=3+: Resolves deeper nesting

## How It Works

1. **Load**: Fetches the document from URL/file
2. **Expand**: Recursively expands all nested `@context` references
3. **Compact**: Re-compacts using the original context
4. **Extract**: Returns just the `@context` object

## Examples

### Schema.org Context

```python
with LdrClient(auto_start_server=True) as client:
    context = client.context("https://schema.org/", depth=2)
    
    # Result includes all schema.org terms
    print(context.keys())
    # ['@vocab', 'name', 'description', 'Person', 'Thing', ...]
```

### Local Development with Mappings

```python
with LdrClient(auto_start_server=True) as client:
    # Map remote URL to local development copy
    client.set_mappings({
        "https://example.com/*": "/home/user/contexts/${rest}"
    })
    
    # This now loads from /home/user/contexts/mycontext.jsonld
    context = client.context("https://example.com/mycontext.jsonld")
```

### Compare Context Depths

```python
with LdrClient(auto_start_server=True) as client:
    shallow = client.context("https://schema.org/", depth=1)
    deep = client.context("https://schema.org/", depth=3)
    
    print(f"Depth 1: {len(shallow)} terms")
    print(f"Depth 3: {len(deep)} terms")
```

## Caching

- Contexts are cached in-memory by (url, depth)
- Check cache: `client.cache_stats()`
- Clear cache: `client.cache_clear()`
- Cache persists across requests when using server mode

## Error Handling

```python
try:
    context = client.context("https://example.com/context.jsonld", depth=3)
except Exception as e:
    print(f"Failed to load context: {e}")
    
    # Use debug_url to diagnose
    client.debug_url("https://example.com/context.jsonld")
```

## See Also

- Full examples: `examples/get_context_example.py`
- API docs: `docs/API.md`
- Mappings guide: `docs/MAPPINGS.md`
