# LDR API Documentation

## Python Client Library

### Installation

```python
from lib.ldr_client import LdrClient
```

### Basic Usage

```python
# Create client
client = LdrClient("http://localhost:3000")

# Compact (recommended - resolves all references)
result = client.compact("https://example.com/data.jsonld", depth=3)

# Expand
result = client.expand("https://example.com/data.jsonld", depth=2)

# Close when done
client.close()
```

### Context Manager (Recommended)

```python
with LdrClient() as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
    # Client automatically closed
```

### Multiple Requests

```python
from lib.ldr_client import LdrClient

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
  "cached": false
}
```

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
  "cached": false
}
```

### GET /health

Health check.

**Response:**
```json
{
  "status": "ok",
  "cache_size": 5
}
```

### GET /cache/stats

Cache statistics.

**Response:**
```json
{
  "size": 5,
  "keys": ["compact:https://...:3"]
}
```

### GET /cache/list

List cached URLs.

**Response:**
```json
{
  "count": 5,
  "urls": ["compact:https://...:3"]
}
```

### DELETE /cache

Clear cache.

**Response:**
```json
{
  "cleared": 5
}
```

## Error Handling

```python
from lib.ldr_client import LdrClient
import requests

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
