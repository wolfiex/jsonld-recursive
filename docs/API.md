<<<<<<< HEAD
<<<<<<< HEAD
# API Documentation

Complete usage examples for jsonld-recursive.

## Python Client
=======
# LDR API Documentation
=======
# API Documentation
>>>>>>> 55f424d (api mappings)

Complete usage examples for jsonld-recursive.

<<<<<<< HEAD
### Installation

```python
from lib.ldr_client import LdrClient
```
>>>>>>> 7e7799a (v1 no local files)
=======
## Python Client
>>>>>>> 55f424d (api mappings)

### Basic Usage

```python
<<<<<<< HEAD
<<<<<<< HEAD
from jsonld_recursive import LdrClient
=======
=======
>>>>>>> 9e5b926 ( docs API)
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
=======
from lib.ldr_client import LdrClient

# Connect to running server
>>>>>>> 55f424d (api mappings)
client = LdrClient("http://localhost:3000")

# Compact document
result = client.compact("https://example.com/data.jsonld", depth=3)
print(result)

# Expand document
result = client.expand("https://example.com/data.jsonld", depth=2)
<<<<<<< HEAD
>>>>>>> 7e7799a (v1 no local files)
=======
print(result)
>>>>>>> 55f424d (api mappings)

# Close when done
client.close()
```

### Context Manager (Recommended)

```python
with LdrClient() as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
<<<<<<< HEAD
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
=======
    print(result)
# Client automatically closed
```

## Auto-Start Server (Recommended)

The easiest way to use the client - it handles server lifecycle automatically!

### Basic Auto-Start
>>>>>>> 55f424d (api mappings)

```python
from jsonld_recursive import LdrClient

<<<<<<< HEAD
<<<<<<< HEAD
# Server starts automatically
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 55f424d (api mappings)
>>>>>>> 9e5b926 ( docs API)
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
<<<<<<< HEAD
    
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
=======
>>>>>>> 55f424d (api mappings)
    
    # This chains through both mappings
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    # Loads from: /home/user/local/experiment/graph.jsonld
```

### Load Mappings from File

```python
with LdrClient(auto_start_server=True) as client:
    # Load mappings at runtime
    client.load_mappings("mappings.json")
    
    result = client.compact("prefix:data.jsonld", depth=3)
```

### Get Current Mappings

```python
with LdrClient(auto_start_server=True) as client:
    mappings = client.get_mappings()
    print(mappings)
```

### Clear Mappings

```python
with LdrClient(auto_start_server=True) as client:
    client.clear_mappings()
```

## Cache Management

### Check Cache Statistics

```python
with LdrClient(auto_start_server=True) as client:
    stats = client.cache_stats()
    print(f"Cache size: {stats['size']}")
    print(f"Cached keys: {stats['keys']}")
```

### List Cached URLs

```python
with LdrClient(auto_start_server=True) as client:
    cached = client.cache_list()
    print(f"Total cached: {cached['count']}")
    
    for url in cached['urls']:
        print(f"  - {url}")
```

### Clear Cache

```python
with LdrClient(auto_start_server=True) as client:
    result = client.cache_clear()
    print(f"Cleared {result['cleared']} entries")
```

## Complete Examples

### Example 1: Simple Script

```python
from lib.ldr_client import LdrClient

# Auto-start server
with LdrClient(auto_start_server=True) as client:
    # Compact document
    result = client.compact("https://example.com/data.jsonld", depth=3)
    
    # Save to file
    import json
    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Saved to output.json")
```

### Example 2: Batch Processing

```python
from lib.ldr_client import LdrClient
import json

def process_batch(urls, mappings_file='mappings.json'):
    """Process multiple URLs with caching."""
    
    with LdrClient(
        auto_start_server=True,
        mappings_file=mappings_file
    ) as client:
        results = []
        
        for url in urls:
            try:
                result = client.compact(url, depth=3)
                results.append({
                    'url': url,
                    'status': 'success',
                    'data': result
                })
                print(f"✓ {url}")
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"✗ {url}: {e}")
        
        # Show cache performance
        stats = client.cache_stats()
        print(f"\nCache entries: {stats['size']}")
        
        # Save results
        with open('batch-results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results

# Use it
urls = [
    "https://example.com/doc1.jsonld",
    "https://example.com/doc2.jsonld",
    "https://example.com/doc3.jsonld"
]

results = process_batch(urls)
print(f"\nProcessed {len(results)} documents")
```

### Example 3: Jupyter Notebook

```python
# Cell 1: Setup
from lib.ldr_client import LdrClient

client = LdrClient(
    auto_start_server=True,
    mappings_file='mappings.json'
)

# Cell 2: Load and explore
result = client.compact("https://example.com/data.jsonld", depth=3)
result  # Jupyter will display nicely

# Cell 3: Multiple documents
urls = ["url1", "url2", "url3"]
results = [client.compact(url, depth=3) for url in urls]

# Cell 4: Cache stats
stats = client.cache_stats()
print(f"Cache size: {stats['size']}")

# Last cell: Cleanup
client.stop_server()
```

### Example 4: With Custom Configuration

```python
from lib.ldr_client import LdrClient

# Start with configuration
with LdrClient(
    base_url="http://localhost:3000",
    auto_start_server=True,
    mappings_file='mappings.json'
) as client:
    
    # Load additional mappings
    client.set_mappings({
        "https://schema.org/*": "./cache/schema/${rest}"
    })
    
    # Process with all optimizations
    result = client.compact("https://example.com/data.jsonld", depth=3)
    
    # Check what mappings are active
    mappings = client.get_mappings()
    print(mappings)
    
    # Monitor cache
    stats = client.cache_stats()
    print(f"Cache: {stats['size']} entries")
```

### Example 5: Data Pipeline

```python
from lib.ldr_client import LdrClient
import pandas as pd
import json

def create_dataset(url_list, output_csv='dataset.csv'):
    """Create dataset from JSON-LD URLs."""
    
    with LdrClient(auto_start_server=True) as client:
        records = []
        
        for url in url_list:
            result = client.compact(url, depth=3)
            
            # Extract relevant fields
            record = {
                'id': result.get('@id'),
                'type': result.get('@type'),
                # Extract other fields...
            }
            records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        df.to_csv(output_csv, index=False)
        
        print(f"Created dataset with {len(records)} records")
        
        # Show cache efficiency
        stats = client.cache_stats()
        print(f"Cache entries: {stats['size']}")
        
        return df

# Use it
urls = ["url1", "url2", "url3"]
df = create_dataset(urls)
```

### Example 6: Process Entire Directory

```python
from pathlib import Path
from lib.ldr_client import LdrClient

with LdrClient(auto_start_server=True) as client:
    # Set up local file mappings
    client.set_mappings({
        "data:*": "/home/user/jsonld-files/${rest}"
    })
    
    # Process all .jsonld files
    data_dir = Path("/home/user/jsonld-files")
    for jsonld_file in data_dir.glob("**/*.jsonld"):
        relative = jsonld_file.relative_to(data_dir)
        url = f"data:{relative}"
        
        try:
            result = client.compact(url, depth=3)
            print(f"✓ {relative}")
        except Exception as e:
            print(f"✗ {relative}: {e}")
```

## Browser JavaScript

### CDN Usage

```html
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>

<script>
  (async () => {
    // Compact
    const compacted = await JsonLdExpand.compact(
      'https://example.com/data.jsonld',
      { depth: 3 }
    );
    console.log(compacted);
    
    // Expand
    const expanded = await JsonLdExpand.expand(
      'https://example.com/data.jsonld',
      { depth: 2 }
    );
    console.log(expanded);
  })();
</script>
```

### With URL Mappings

```html
<script>
  (async () => {
    const mappings = {
      'cmip7:*': 'https://wcrp-cmip.github.io/CMIP7-CVs/${rest}',
      'https://wcrp-cmip.github.io/CMIP7-CVs/*': 'https://cdn.example.com/${rest}'
    };
    
    const result = await JsonLdExpand.compact(
      'cmip7:experiment/graph.jsonld',
      { depth: 3, mappings }
    );
    
    console.log(result);
  })();
</script>
```

### Interactive Document Viewer

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>
</head>
<body>
  <input type="text" id="url" placeholder="Enter JSON-LD URL">
  <input type="number" id="depth" value="3" min="1" max="10">
  <button onclick="loadDocument()">Load</button>
  <pre id="output"></pre>

  <script>
    async function loadDocument() {
      const url = document.getElementById('url').value;
      const depth = parseInt(document.getElementById('depth').value);
      
      try {
        const result = await JsonLdExpand.compact(url, { depth });
        document.getElementById('output').textContent = 
          JSON.stringify(result, null, 2);
      } catch (error) {
        document.getElementById('output').textContent = 
          `Error: ${error.message}`;
      }
    }
  </script>
</body>
</html>
```

## HTTP API

### POST /compact

Compact a JSON-LD document (recommended).

```bash
curl -X POST http://localhost:3000/compact \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/data.jsonld",
    "depth": 3
  }'
```

Response:
```json
{
<<<<<<< HEAD
  "result": { ... },
>>>>>>> 7e7799a (v1 no local files)
=======
  "result": { 
    "@context": "...",
    "@graph": [...]
  },
>>>>>>> 55f424d (api mappings)
  "cached": false
}
>>>>>>> 8fa9a5e (merge)
```

<<<<<<< HEAD
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
=======
### POST /expand
>>>>>>> 55f424d (api mappings)

Expand a JSON-LD document.

```bash
curl -X POST http://localhost:3000/expand \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/data.jsonld",
    "depth": 2
  }'
```

Response:
```json
{
<<<<<<< HEAD
  "result": { ... },
>>>>>>> 7e7799a (v1 no local files)
=======
  "result": [...],
>>>>>>> 55f424d (api mappings)
  "cached": false
}
>>>>>>> 8fa9a5e (merge)
```

### GET /health

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 9e5b926 ( docs API)
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
=======
Health check endpoint.
>>>>>>> 55f424d (api mappings)

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "ok",
<<<<<<< HEAD
  "cache_size": 5
>>>>>>> 7e7799a (v1 no local files)
=======
  "cache_size": 5,
  "mappings_count": 2
>>>>>>> 55f424d (api mappings)
}
```

### GET /cache/stats

<<<<<<< HEAD
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
=======
Get cache statistics.
>>>>>>> 55f424d (api mappings)

```bash
curl http://localhost:3000/cache/stats
```

Response:
```json
{
  "size": 5,
<<<<<<< HEAD
  "keys": ["compact:https://...:3"]
>>>>>>> 7e7799a (v1 no local files)
=======
  "keys": [
    "compact:https://example.com/data.jsonld:3",
    "expand:https://example.com/other.jsonld:2"
  ]
>>>>>>> 55f424d (api mappings)
}
```

### GET /cache/list

<<<<<<< HEAD
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
=======
List all cached URLs.
>>>>>>> 55f424d (api mappings)

```bash
curl http://localhost:3000/cache/list
```

Response:
```json
{
  "count": 5,
<<<<<<< HEAD
  "urls": ["compact:https://...:3"]
>>>>>>> 7e7799a (v1 no local files)
=======
  "urls": [
    "compact:https://example.com/data.jsonld:3",
    "expand:https://example.com/other.jsonld:2"
  ]
>>>>>>> 55f424d (api mappings)
}
```

### DELETE /cache

<<<<<<< HEAD
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
=======
Clear the entire cache.

```bash
curl -X DELETE http://localhost:3000/cache
```

Response:
>>>>>>> 55f424d (api mappings)
```json
{
  "cleared": 5
}
```

<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 8fa9a5e (merge)
=======
<<<<<<< HEAD
=======
>>>>>>> 55f424d (api mappings)
>>>>>>> 9e5b926 ( docs API)
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

<<<<<<< HEAD
=======
>>>>>>> 7e7799a (v1 no local files)
=======
>>>>>>> 55f424d (api mappings)
## Error Handling

```python
from lib.ldr_client import LdrClient
import requests

<<<<<<< HEAD
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
=======
try:
    with LdrClient(auto_start_server=True) as client:
>>>>>>> 55f424d (api mappings)
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
<<<<<<< HEAD
>>>>>>> 7e7799a (v1 no local files)
<<<<<<< HEAD
>>>>>>> 8fa9a5e (merge)
=======
=======

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
```

## See Also

- [CLI.md](CLI.md) - Complete CLI reference
- [MAPPINGS.md](MAPPINGS.md) - Detailed mappings guide
- [examples/example_usage.py](../examples/example_usage.py) - Runnable examples
>>>>>>> 55f424d (api mappings)
>>>>>>> 9e5b926 ( docs API)
