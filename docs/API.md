# API Documentation

Complete usage examples for jsonld-recursive.

## Python Client

### Basic Usage

```python
from lib.ldr_client import LdrClient

# Connect to running server
client = LdrClient("http://localhost:3000")

# Compact document
result = client.compact("https://example.com/data.jsonld", depth=3)
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

The easiest way to use the client - it handles server lifecycle automatically!

### Basic Auto-Start

```python
from lib.ldr_client import LdrClient

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
with LdrClient(auto_start_server=True) as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
    print(result)
# Server automatically stopped
```

### Auto-Start with Mappings File

```python
with LdrClient(
    auto_start_server=True,
    mappings_file="mappings.json"
) as client:
    # Server started with mappings loaded
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    print(result)
```

## Working with URL Mappings

### Set Mappings Programmatically

```python
with LdrClient(auto_start_server=True) as client:
    # Set chained mappings
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
    })
    
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
  "result": { 
    "@context": "...",
    "@graph": [...]
  },
  "cached": false
}
```

### POST /expand

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
  "result": [...],
  "cached": false
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "ok",
  "cache_size": 5,
  "mappings_count": 2
}
```

### GET /cache/stats

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
}
```

### GET /cache/list

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
}
```

### DELETE /cache

Clear the entire cache.

```bash
curl -X DELETE http://localhost:3000/cache
```

Response:
```json
{
  "cleared": 5
}
```

### GET /mappings

Get current URL mappings.

```bash
curl http://localhost:3000/mappings
```

Response:
```json
{
  "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
  "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
}
```

### POST /mappings

Set URL mappings.

```bash
curl -X POST http://localhost:3000/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
    "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
  }'
```

Response:
```json
{
  "success": true,
  "count": 2
}
```

### DELETE /mappings

Clear all URL mappings.

```bash
curl -X DELETE http://localhost:3000/mappings
```

Response:
```json
{
  "success": true,
  "cleared": 2
}
```

## CLI Usage

See [CLI.md](CLI.md) for complete CLI reference.

### Basic Commands

```bash
# Compact (standalone, no server)
ldr compact https://example.com/data.jsonld -d 3

# Compact (using server for caching)
ldr compact https://example.com/data.jsonld -d 3 --server

# Expand
ldr expand https://example.com/data.jsonld -d 2
```

### Server Management

```bash
# Start server
ldr server start

# Start with custom port
ldr server start 8080

# Start with mappings
ldr server start 3000 mappings.json

# Stop server
ldr server stop
```

### Mappings Management

```bash
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

## Error Handling

```python
from lib.ldr_client import LdrClient
import requests

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
```

## See Also

- [CLI.md](CLI.md) - Complete CLI reference
- [MAPPINGS.md](MAPPINGS.md) - Detailed mappings guide
- [examples/example_usage.py](../examples/example_usage.py) - Runnable examples
