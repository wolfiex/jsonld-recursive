# jsonld-recursive

Recursively expand and compact JSON-LD documents with caching and chained URL mappings.

## Installation

```bash
npm install jsonld-recursive
```

## Quick Start

### CLI

```bash
# Standalone
ldr compact https://example.com/data.jsonld -d 3

# With server
ldr server start
ldr compact https://example.com/data.jsonld -d 3 --server
ldr server stop
```

### Python

```python
from lib.ldr_client import LdrClient

# Auto-start server
with LdrClient(auto_start_server=True) as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
```

### Browser (CDN)

```html
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>

<script>
  await JsonLdExpand.compact('https://example.com/data.jsonld', {depth: 3});
</script>
```

## Server Commands

```bash
# Start
ldr server start

# Start with port
ldr server start 8080

# Start with mappings file
ldr server start 3000 mappings.json

# Start with JSON mappings
ldr server start 3000 '{"cmip7:*":"https://example.com/${rest}"}'

# Stop
ldr server stop

# Status
ldr server status

# Or kill by name
pkill ldr-server
```

## Chained URL Mappings

Apply multiple mappings in sequence:

```json
{
  "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
  "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local-cvs/${rest}"
}
```

**Input:** `cmip7:experiment/graph.jsonld`  
**Step 1:** `cmip7:*` → `https://wcrp-cmip.github.io/CMIP7-CVs/experiment/graph.jsonld`  
**Step 2:** `https://.../*` → `/home/user/local-cvs/experiment/graph.jsonld`  
**Result:** Loads from local file

### Set Mappings

**CLI:**
```bash
# From file
ldr mappings set mappings.json

# From JSON (no -m flag needed)
ldr mappings set '{"cmip7:*":"https://example.com/${rest}"}'

# Get current
ldr mappings get

# Clear
ldr mappings clear
```

**Python:**
```python
with LdrClient(auto_start_server=True) as client:
    # Set chained mappings
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local-cvs/${rest}"
    })
    
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
```

## Python Client

### Basic Usage

```python
from lib.ldr_client import LdrClient

with LdrClient() as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
```

### Auto-start Server

```python
# Server starts and stops automatically
with LdrClient(auto_start_server=True) as client:
    result = client.compact("https://example.com/data.jsonld", depth=3)
```

### Multiple Requests

```python
with LdrClient(auto_start_server=True) as client:
    urls = ["url1", "url2", "url3"]
    
    # Loop
    for url in urls:
        result = client.compact(url, depth=3)
    
    # Or batch
    results = client.compact_batch(urls, depth=3)
```

### Runtime Mappings

```python
with LdrClient(auto_start_server=True) as client:
    # Set mappings
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local/${rest}"
    })
    
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    
    # Update
    client.set_mappings({"new:*": "https://new.com/${rest}"})
    
    # Clear
    client.clear_mappings()
```

## CLI Usage

```bash
# Standalone (no server)
ldr compact <url> -d 3

# With server (caching)
ldr compact <url> -d 3 --server

# Server management
ldr server start [port] [mappings.json]
ldr server stop
ldr server status

# Mappings (server must be running)
ldr mappings get
ldr mappings set mappings.json
ldr mappings set '{"prefix:*":"https://example.com/${rest}"}'
ldr mappings clear
```

## Documentation

- [docs/API.md](docs/API.md) - Full API reference
- [docs/MAPPINGS.md](docs/MAPPINGS.md) - Detailed mappings guide
- [example_script.py](example_script.py) - Python example

## Publishing

```bash
npm login
npm publish
```

After publishing, available via CDN:
- `https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js`
- `https://unpkg.com/jsonld-recursive@1/lib/ldr-core.js`

## License

MIT
