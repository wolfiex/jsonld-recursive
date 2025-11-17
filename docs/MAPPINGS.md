# URL Mappings

URL mappings allow you to redirect requests during JSON-LD expansion with chaining support.

## Chained Mappings

Mappings are applied **repeatedly** until no more matches are found:

```json
{
  "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
  "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local-cvs/${rest}"
}
```

**Example:**
- Input: `cmip7:experiment/graph.jsonld`
- Step 1: Match `cmip7:*` → `https://wcrp-cmip.github.io/CMIP7-CVs/experiment/graph.jsonld`
- Step 2: Match `https://wcrp-cmip.github.io/CMIP7-CVs/*` → `/home/user/local-cvs/experiment/graph.jsonld`
- Final: Loads from local file

## Wildcard Patterns

Use `*` to match any characters and `${rest}` to capture:

```json
{
  "https://old.com/*": "https://new.com/${rest}",
  "prefix:*": "https://example.com/${rest}"
}
```

## CLI Usage

### Start Server with Mappings

```bash
# With file
ldr server start 3000 mappings.json

# With JSON
ldr server start 3000 '{"cmip7:*":"https://example.com/${rest}"}'

# Just port
ldr server start 8080

# Default port (3000)
ldr server start
```

### Update Mappings at Runtime

```bash
# From file
ldr mappings set mappings.json

# From JSON string
ldr mappings set '{"cmip7:*":"https://wcrp-cmip.github.io/CMIP7-CVs/${rest}"}'

# Get current mappings
ldr mappings get

# Clear mappings
ldr mappings clear
```

## Python Usage

### Set Mappings

```python
from lib.ldr_client import LdrClient

# From file at startup
with LdrClient(auto_start_server=True, mappings_file="mappings.json") as client:
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)

# Set programmatically
with LdrClient() as client:
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/local-cvs/${rest}"
    })
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)

# Load from file at runtime
client.load_mappings("mappings.json")

# Get mappings
mappings = client.get_mappings()

# Clear mappings
client.clear_mappings()
```

## Mapping Examples

### Example 1: Custom Prefix to Local Files

```json
{
  "mydata:*": "https://api.example.com/${rest}",
  "https://api.example.com/*": "/home/user/data/${rest}"
}
```

**Input:** `mydata:users/123.jsonld`  
**Chain:**
1. `mydata:*` → `https://api.example.com/users/123.jsonld`
2. `https://api.example.com/*` → `/home/user/data/users/123.jsonld`

### Example 2: Remote to Local Development

```json
{
  "https://production.example.com/*": "http://localhost:8080/${rest}",
  "http://localhost:8080/*": "/home/user/dev/api/${rest}"
}
```

### Example 3: Multi-step Resolution

```json
{
  "vocab:*": "https://vocabs.org/${rest}",
  "https://vocabs.org/*": "https://cdn.vocabs.org/${rest}",
  "https://cdn.vocabs.org/*": "/home/user/vocab-cache/${rest}"
}
```

## Complete Example

**mappings.json:**
```json
{
  "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
  "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/CMIP7-CVs/${rest}"
}
```

**Python:**
```python
from lib.ldr_client import LdrClient

with LdrClient(auto_start_server=True) as client:
    # Set chained mappings
    client.set_mappings({
        "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
        "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/home/user/CMIP7-CVs/${rest}"
    })
    
    # This URL chains through both mappings
    result = client.compact("cmip7:experiment/graph.jsonld", depth=3)
    # Fetches from: /home/user/CMIP7-CVs/experiment/graph.jsonld
```

**CLI:**
```bash
# Start with mappings
ldr server start 3000 mappings.json

# Or set at runtime
ldr server start
ldr mappings set mappings.json
ldr compact cmip7:experiment/graph.jsonld -d 3 --server
```

## File Protocol Support

Mappings can resolve to local files:

```json
{
  "https://remote.com/*": "/home/user/local-files/${rest}",
  "https://other.com/*": "file:///path/to/files/${rest}"
}
```

Both `/path/to/file` and `file:///path/to/file` work.

## Runtime Updates

### Python

```python
with LdrClient(auto_start_server=True) as client:
    # Initial mappings
    client.set_mappings({
        "prefix1:*": "https://example.com/${rest}"
    })
    
    # Process some URLs
    result = client.compact("prefix1:data.jsonld", depth=3)
    
    # Update mappings
    client.set_mappings({
        "prefix1:*": "https://example.com/${rest}",
        "prefix2:*": "https://other.com/${rest}"
    })
    
    # Clear when done
    client.clear_mappings()
```

### CLI

```bash
ldr server start
ldr mappings set '{"cmip7:*":"https://example.com/${rest}"}'
ldr compact cmip7:data.jsonld -d 3 --server
ldr mappings set '{"other:*":"https://other.com/${rest}"}'
ldr mappings clear
```

## Debugging

Server logs show the full mapping chain:

```
Mapping chain: cmip7:experiment/graph.jsonld -> /home/user/CMIP7-CVs/experiment/graph.jsonld
```

## Max Depth

Chaining stops after 10 iterations to prevent infinite loops. If you hit this limit, check for circular mappings.
