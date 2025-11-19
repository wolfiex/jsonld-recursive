<<<<<<< HEAD
# API Documentation

Complete usage examples for jsonld-recursive.

## Python Client
=======
# LDR API Documentation

## Python Client Library

### Installation

```python
from lib.ldr_client import LdrClient
```
>>>>>>> 7e7799a (v1 no local files)

### Basic Usage

```python
<<<<<<< HEAD
from jsonld_recursive import LdrClient
=======
<<<<<<< HEAD
from lib.ldr_client import LdrClient
>>>>>>> 8fa9a5e (merge)

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
=======
# Create client
client = LdrClient("http://localhost:3000")

# Compact (recommended - resolves all references)
result = client.compact("https://example.com/data.jsonld", depth=3)

# Expand
result = client.expand("https://example.com/data.jsonld", depth=2)
>>>>>>> 7e7799a (v1 no local files)

# Close when done
client.close()
```

### Context Manager (Recommended)

```python
with LdrClient() as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
<<<<<<< HEAD
    print(result)
# Client automatically closed
```

## Auto-Start Server (Recommended)

### Basic Auto-Start
=======
    # Client automatically closed
```

### Multiple Requests
>>>>>>> 7e7799a (v1 no local files)

```python
from jsonld_recursive import LdrClient

<<<<<<< HEAD
# Server starts automatically
=======
<<<<<<< HEAD
# Server starts automatically when created
client = LdrClient(auto_start_server=True)

# Use the client
result = client.compact("https://example.com/data.jsonld", depth=3)
print(result)

# Stop when done
client.stop_server()
```

### Auto-Start with Context Manager (Best Practice)

```python
# Server starts and stops automatically!
>>>>>>> 8fa9a5e (merge)
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
<<<<<<< HEAD
  -d '{"url": "https://example.com/data.jsonld", "depth": 3}'
=======
  -d '{
    "url": "https://example.com/data.jsonld",
    "depth": 3
  }'
```

Response:
```json
{
  "result": { 
    "@context": "...",
    "@graph": [...]
  },
=======
# Client reuses connections (connection pooling)
with LdrClient() as client:
    urls = [
        "https://example.com/1.jsonld",
        "https://example.com/2.jsonld",
        "https://example.com/3.jsonld"
    ]
    
    results = []
    for url in urls:
        result = client.compact(url, depth=3)
        results.append(result)
```

### Batch Processing

```python
with LdrClient() as client:
    urls = ["url1", "url2", "url3"]
    results = client.compact_batch(urls, depth=3)
```

### Cache Operations

```python
with LdrClient() as client:
    # Get cache stats
    stats = client.cache_stats()
    print(f"Cache has {stats['size']} entries")
    
    # List cached URLs
    cached = client.cache_list()
    print(f"Cached {cached['count']} URLs")
    
    # Clear cache
    cleared = client.cache_clear()
```

### Configuration

```python
client = LdrClient(
    base_url="http://localhost:3000",  # Server URL
    timeout=30,                         # Request timeout (seconds)
    max_retries=3                       # Max retries for failed requests
)
```

### Silent Mode

```python
# Disable cache hit/miss messages
result = client.compact("https://example.com/data.jsonld", depth=3, verbose=False)
```

## HTTP API Endpoints

### POST /expand

Expand JSON-LD document.

**Request:**
```json
{
  "url": "https://example.com/data.jsonld",
  "depth": 3
}
```

**Response:**
```json
{
  "result": { ... },
>>>>>>> 7e7799a (v1 no local files)
  "cached": false
}
>>>>>>> 8fa9a5e (merge)
```

<<<<<<< HEAD
### POST /expand

```bash
curl -X POST http://localhost:3000/expand \
  -H "Content-Type: application/json" \
<<<<<<< HEAD
  -d '{"url": "https://example.com/data.jsonld", "depth": 2}'
=======
  -d '{
    "url": "https://example.com/data.jsonld",
    "depth": 2
  }'
```

Response:
```json
{
  "result": [...],
=======
### POST /compact

Compact JSON-LD document (recommended).

**Request:**
```json
{
  "url": "https://example.com/data.jsonld",
  "depth": 3
}
```

**Response:**
```json
{
  "result": { ... },
>>>>>>> 7e7799a (v1 no local files)
  "cached": false
}
>>>>>>> 8fa9a5e (merge)
```

### GET /health

<<<<<<< HEAD
=======
<<<<<<< HEAD
Health check endpoint.

>>>>>>> 8fa9a5e (merge)
```bash
curl http://localhost:3000/health
```

<<<<<<< HEAD
=======
Response:
```json
{
  "status": "ok",
  "cache_size": 5,
  "mappings_count": 2
=======
Health check.

**Response:**
```json
{
  "status": "ok",
  "cache_size": 5
>>>>>>> 7e7799a (v1 no local files)
}
```

### GET /cache/stats

<<<<<<< HEAD
Get cache statistics.

```bash
curl http://localhost:3000/cache/stats
```

Response:
```json
{
  "size": 5,
  "keys": [
    "compact:https://example.com/data.jsonld:3",
    "expand:https://example.com/other.jsonld:2"
  ]
=======
Cache statistics.

**Response:**
```json
{
  "size": 5,
  "keys": ["compact:https://...:3"]
>>>>>>> 7e7799a (v1 no local files)
}
```

### GET /cache/list

<<<<<<< HEAD
List all cached URLs.

```bash
curl http://localhost:3000/cache/list
```

Response:
```json
{
  "count": 5,
  "urls": [
    "compact:https://example.com/data.jsonld:3",
    "expand:https://example.com/other.jsonld:2"
  ]
=======
List cached URLs.

**Response:**
```json
{
  "count": 5,
  "urls": ["compact:https://...:3"]
>>>>>>> 7e7799a (v1 no local files)
}
```

### DELETE /cache

<<<<<<< HEAD
Clear the entire cache.

```bash
curl -X DELETE http://localhost:3000/cache
```

Response:
=======
Clear cache.

**Response:**
>>>>>>> 7e7799a (v1 no local files)
```json
{
  "cleared": 5
}
```

<<<<<<< HEAD
>>>>>>> 8fa9a5e (merge)
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
<<<<<<< HEAD
curl -X DELETE http://localhost:3000/cache
=======
# Set from file
ldr mappings set mappings.json

# Set from JSON
ldr mappings set '{"cmip7:*":"https://example.com/${rest}"}'

# Get current
ldr mappings get

# Clear
ldr mappings clear
```

## API Reference

### LdrClient

#### Constructor

```python
LdrClient(
    base_url="http://localhost:3000",
    timeout=30,
    max_retries=3,
    auto_start_server=False,
    mappings_file=None
)
```

#### Methods

**compact(url, depth=2)**
```python
result = client.compact("https://example.com/data.jsonld", depth=3)
```

**expand(url, depth=2)**
```python
result = client.expand("https://example.com/data.jsonld", depth=2)
```

**compact_batch(urls, depth=2)**
```python
results = client.compact_batch(["url1", "url2", "url3"], depth=3)
```

**set_mappings(mappings)**
```python
client.set_mappings({
    "prefix:*": "https://example.com/${rest}"
})
```

**load_mappings(filepath)**
```python
client.load_mappings("mappings.json")
```

**get_mappings()**
```python
mappings = client.get_mappings()
```

**clear_mappings()**
```python
client.clear_mappings()
```

**cache_stats()**
```python
stats = client.cache_stats()
```

**cache_list()**
```python
cached = client.cache_list()
```

**cache_clear()**
```python
result = client.cache_clear()
```

**stop_server()**
```python
client.stop_server()  # Only for auto-started servers
```

**close()**
```python
client.close()  # Close HTTP session
```

=======
>>>>>>> 7e7799a (v1 no local files)
## Error Handling

```python
from lib.ldr_client import LdrClient
import requests

<<<<<<< HEAD
try:
    with LdrClient(auto_start_server=True) as client:
        result = client.compact("https://example.com/data.jsonld", depth=3)
        print(result)
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to server")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Tips & Best Practices

### 1. Always Use Context Manager

```python
# Good - auto cleanup
with LdrClient(auto_start_server=True) as client:
    result = client.compact(url, depth=3)

# Less good - manual cleanup needed
client = LdrClient(auto_start_server=True)
result = client.compact(url, depth=3)
client.stop_server()  # Don't forget!
```

### 2. Reuse Client Instance

```python
# Good - reuse connection
with LdrClient(auto_start_server=True) as client:
    for url in urls:
        result = client.compact(url, depth=3)

# Bad - creates new connection each time
for url in urls:
    with LdrClient(auto_start_server=True) as client:
        result = client.compact(url, depth=3)
```

### 3. Monitor Cache Performance

```python
with LdrClient(auto_start_server=True) as client:
    # Process documents
    for url in urls:
        client.compact(url, depth=3)
    
    # Check cache
    stats = client.cache_stats()
    print(f"Cache entries: {stats['size']}")
```

### 4. Use Mappings for Offline Work

```python
# Download files once, then use cached versions
with LdrClient(
    auto_start_server=True,
    mappings_file='url-map.json'  # Maps URLs to ./cache/
) as client:
    # All requests use local cache
    result = client.compact("https://example.com/data.jsonld", depth=3)
>>>>>>> 8fa9a5e (merge)
```

## See Also

- [MAPPINGS.md](MAPPINGS.md) - Detailed mappings guide
<<<<<<< HEAD
- [examples/example_usage.py](../examples/example_usage.py) - Python examples
=======
- [examples/example_usage.py](../examples/example_usage.py) - Runnable examples
=======
with LdrClient() as client:
    try:
        result = client.compact("https://example.com/data.jsonld", depth=3)
    except requests.exceptions.ConnectionError:
        print("Server not running")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
```

## Server Management

```bash
# Start server
node ldr-server.js

# Stop server
pkill ldr-server

# Check if running
ps aux | grep ldr-server

# Custom port
PORT=8080 node ldr-server.js
```
>>>>>>> 7e7799a (v1 no local files)
>>>>>>> 8fa9a5e (merge)
