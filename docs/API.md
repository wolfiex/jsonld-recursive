# API Documentation

Complete usage examples for jsonld-recursive.

## Python Client

### Basic Usage

```python
from jsonld_recursive import LdrClient

# Connect to running server
client = LdrClient("http://localhost:3000")

# Compact document
result = client.compact("https://example.com/data.jsonld", depth=3)
print(result)

# Compact local file
result = client.compact("/path/to/data.jsonld", depth=3)
print(result)

# Expand document
result = client.expand("https://example.com/data.jsonld", depth=2)
print(result)

# Close when done
client.close()
```

### Context Manager (Recommended)

```python
with LdrClient() as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
    print(result)
# Client automatically closed
```

## Auto-Start Server (Recommended)

### Basic Auto-Start

```python
from jsonld_recursive import LdrClient

# Server starts automatically
with LdrClient(auto_start_server=True) as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
    print(result)
# Server automatically stopped
```

### With Mappings Dictionary

```python
with LdrClient(
    auto_start_server=True,
    mappings={
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
    }
) as client:
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    print(result)
```

### With Mappings File

```python
with LdrClient(
    auto_start_server=True,
    mappings_file="mappings.json"
) as client:
    result = client.compact("prefix:data.jsonld", depth=3)
    print(result)
```

## URL Mappings

### Set Mappings

```python
with LdrClient(auto_start_server=True) as client:
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
    })
    
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
```

### Load from File

```python
with LdrClient(auto_start_server=True) as client:
    client.load_mappings("mappings.json")
    result = client.compact("prefix:data.jsonld", depth=3)
```

### Get and Clear

```python
with LdrClient(auto_start_server=True) as client:
    # Get current mappings
    mappings = client.get_mappings()
    print(mappings)
    
    # Clear all mappings
    client.clear_mappings()
```

## Cache Management

### Statistics

```python
with LdrClient(auto_start_server=True) as client:
    stats = client.cache_stats()
    print(f"Cache size: {stats['size']}")
    print(f"Cached keys: {stats['keys']}")
```

### List and Clear

```python
with LdrClient(auto_start_server=True) as client:
    # List all cached URLs
    cached = client.cache_list()
    print(f"Total: {cached['count']}")
    for url in cached['urls']:
        print(f"  - {url}")
    
    # Clear cache
    result = client.cache_clear()
    print(f"Cleared {result} entries")
```

## Complete Examples

### Batch Processing

```python
from jsonld_recursive import LdrClient

urls = [
    "https://example.com/doc1.jsonld",
    "https://example.com/doc2.jsonld",
    "https://example.com/doc3.jsonld"
]

with LdrClient(auto_start_server=True) as client:
    results = client.compact_batch(urls, depth=3)
    print(f"Processed {len(results)} documents")
```

### With Local Files

```python
from pathlib import Path
from jsonld_recursive import LdrClient

with LdrClient(auto_start_server=True) as client:
    for file in Path("./data").glob("*.jsonld"):
        result = client.compact(str(file), depth=3)
        print(f"✓ {file}")
```

## Browser JavaScript

### CDN Usage

```html
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>

<script>
  (async () => {
    const result = await JsonLdExpand.compact(
      'https://example.com/data.jsonld',
      { depth: 3 }
    );
    console.log(result);
  })();
</script>
```

## HTTP API

### POST /compact

```bash
curl -X POST http://localhost:3000/compact \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/data.jsonld", "depth": 3}'
```

### POST /expand

```bash
curl -X POST http://localhost:3000/expand \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/data.jsonld", "depth": 2}'
```

### GET /health

```bash
curl http://localhost:3000/health
```

### GET /mappings

```bash
curl http://localhost:3000/mappings
```

### POST /mappings

```bash
curl -X POST http://localhost:3000/mappings \
  -H "Content-Type: application/json" \
  -d '{"mappings": {"prefix:*": "https://example.com/${rest}"}}'
```

### DELETE /mappings

```bash
curl -X DELETE http://localhost:3000/mappings
```

### GET /cache/stats

```bash
curl http://localhost:3000/cache/stats
```

### GET /cache/list

```bash
curl http://localhost:3000/cache/list
```

### DELETE /cache

```bash
curl -X DELETE http://localhost:3000/cache
```

## See Also

- [MAPPINGS.md](MAPPINGS.md) - Detailed mappings guide
- [examples/example_usage.py](../examples/example_usage.py) - Python examples
