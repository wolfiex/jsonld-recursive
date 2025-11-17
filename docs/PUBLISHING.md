# Publishing to npm

## Pre-publish Checklist

1. ✅ Update `package.json`:
   - Set `name` (must be unique on npm)
   - Set `version` 
   - Set `author`
   - Set `repository` URL
   - Set `homepage` URL

2. ✅ Test locally:
   ```bash
   npm install
   npm link
   ldr compact https://example.com/data.jsonld -d 3
   npm unlink
   ```

3. ✅ Check what will be published:
   ```bash
   npm pack --dry-run
   ```

## Publishing Steps

### First Time

```bash
# Login to npm
npm login

# Publish
npm publish

# If name is scoped (@yourname/jsonld-recursive)
npm publish --access public
```

### Updates

```bash
# Update version
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0

# Publish
npm publish
```

## After Publishing

Your package will be available:

### npm
```bash
npm install jsonld-recursive
```

### CDN (automatic)
```html
<!-- jsDelivr -->
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jsonld-recursive@1/lib/ldr-browser.js"></script>

<!-- unpkg -->
<script src="https://unpkg.com/jsonld-recursive@1/lib/ldr-core.js"></script>
<script src="https://unpkg.com/jsonld-recursive@1/lib/ldr-browser.js"></script>
```

### CLI (global)
```bash
npm install -g jsonld-recursive
ldr compact https://example.com/data.jsonld -d 3
```

## What Gets Published

Files specified in `package.json` "files" array:
- `lib/` - Core library files
- `docs/` - Documentation
- `ldr` - CLI executable
- `ldr-server.js` - Server
- `example.html` - Browser demo
- `mappings.example.json` - Example mappings
- `README.md` - Main documentation

**Not published** (in .npmignore):
- Python files (*.py)
- Node modules
- Cache files
- Git files

## Verify Package

After publishing, test installation:

```bash
# In a different directory
npm install jsonld-recursive

# Test CLI
npx ldr compact https://example.com/data.jsonld -d 3

# Test in Node.js
node
> const { compactJsonLd } = require('jsonld-recursive')
```

## Package URLs

After publishing as `jsonld-recursive`:

- npm: https://www.npmjs.com/package/jsonld-recursive
- jsDelivr: https://cdn.jsdelivr.net/npm/jsonld-recursive/
- unpkg: https://unpkg.com/jsonld-recursive/
- GitHub: https://github.com/yourusername/jsonld-recursive

## Troubleshooting

### Name already taken
Change `name` in package.json to something unique, or use scoped package:
```json
{
  "name": "@yourusername/jsonld-recursive"
}
```

### Files not included
Check `files` array in package.json and .npmignore

### Version conflict
```bash
npm version patch
npm publish
```
