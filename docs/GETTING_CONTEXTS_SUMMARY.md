# Summary: Getting Compiled Contexts from jsonld-recursive

## What You Can Do

The `jsonld-recursive` package can extract and compile JSON-LD `@context` definitions from:
- Remote URLs (https://, http://)
- Local file paths (absolute or relative)
- URLs with custom mappings (e.g., `prefix:` → `https://...`)

## Three Ways to Get Contexts

### 1. Python (Recommended)

**File: `examples/get_context_example.py`**

```python
from lib.ldr_client import LdrClient

# Simple usage
with LdrClient(auto_start_server=True) as client:
    context = client.context("https://schema.org/", depth=3)
    print(context)
```

**Key Methods:**
- `client.context(url, depth)` - Get compiled context
- `client.set_mappings(mappings)` - Set URL mappings
- `client.cache_stats()` - Check cache performance

### 2. CLI (Command Line)

```bash
# Get context from URL
ldr context https://schema.org/ -d 3

# Save to file
ldr context https://schema.org/ -d 3 > context.json

# With server (enables caching)
ldr server start
ldr context https://schema.org/ -d 3 --server
ldr server stop

# With mappings
ldr server start
ldr mappings set '{"prefix:*":"https://example.com/${rest}"}'
ldr context prefix:data.jsonld -d 3 --server
```

### 3. HTTP API

```bash
curl -X POST http://localhost:3333/context \
  -H "Content-Type: application/json" \
  -d '{"url": "https://schema.org/", "depth": 3}'
```

## How It Works Internally

**Server Code:** `ldr-server.js` (lines 293-330)

1. Receives request: `POST /context` with `{url, depth}`
2. Checks cache: `getCacheKey(url, depth, 'context')`
3. If not cached:
   - Calls `expandRecursive(jsonld, url, depth)` to resolve nested contexts
   - Calls `jsonld.compact(expanded, url)` to compile the context
   - Extracts `@context` from the result
4. Returns compiled context with cache status

**Core Library:** `lib/ldr-core.js`

- `expandRecursive()` - Recursively loads and expands nested @context references
- `compactJsonLd()` - Compacts using original URL, compiling the context
- Custom `documentLoader` - Handles URL mappings and local files

## Key Features

### URL Mappings (Chained)

```javascript
{
  "cmip7:*": "https://wcrp-cmip.github.io/CMIP7-CVs/${rest}",
  "https://wcrp-cmip.github.io/CMIP7-CVs/*": "/local/path/${rest}"
}
```

Input: `cmip7:experiment/context.jsonld`
→ Step 1: `https://wcrp-cmip.github.io/CMIP7-CVs/experiment/context.jsonld`
→ Step 2: `/local/path/experiment/context.jsonld`

### Caching

- In-memory cache (Map)
- Cache key: `context:${url}:${depth}`
- Survives across requests when using server
- Can be cleared: `DELETE /cache` or `client.cache_clear()`

### Local File Support

The custom document loader treats local paths as `file://` URLs, which allows the jsonld library to properly resolve relative @context paths within the document.

## Files Modified/Created

### Modified:
- `ldr` (line 398-408) - Added standalone context support

### Already Implemented:
- `ldr-server.js` (line 293-330) - `/context` endpoint
- `lib/ldr_client.py` (line 470-502) - `context()` method

### Created:
- `examples/get_context_example.py` - Complete working examples
- `docs/CONTEXT.md` - Quick reference guide

## Testing

### CLI Test:
```bash
cd /Users/daniel.ellis/WIPwork/jsonld-recursive
./ldr context https://www.w3.org/ns/activitystreams -d 2
```
✅ Works!

### Python Test:
```bash
python3 examples/get_context_example.py
```

## Next Steps

1. **Test it:**
   ```bash
   cd /Users/daniel.ellis/WIPwork/jsonld-recursive
   python3 examples/get_context_example.py
   ```

2. **Use it in your workflow:**
   ```python
   from lib.ldr_client import LdrClient
   
   with LdrClient(auto_start_server=True) as client:
       context = client.context("your-url-here", depth=3)
   ```

3. **Set up mappings for your data:**
   ```python
   client.set_mappings({
       "your-prefix:*": "https://your-domain.com/${rest}"
   })
   ```

## Documentation

- **Full API**: `docs/API.md`
- **Context Guide**: `docs/CONTEXT.md` (newly created)
- **Mappings**: `docs/MAPPINGS.md`
- **Examples**: `examples/get_context_example.py`

## Summary

Everything you need is already implemented! The key method is:

**Python:** `client.context(url, depth=3)`
**CLI:** `ldr context <url> -d 3`
**HTTP:** `POST /context` with `{url, depth}`

All three methods return just the compiled `@context` object, with recursive resolution of nested contexts up to the specified depth.
