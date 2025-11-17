// ldr-core.js
// Universal JSON-LD recursive expand/compact functions

async function expandRecursive(jsonld, url, maxDepth = 2, currentDepth = 0, visited = new Set()) {
  if (currentDepth >= maxDepth) {
    return { "@id": url };
  }
  
  visited.add(url);
  
  try {
    const expanded = await jsonld.expand(url);
    const doc = Array.isArray(expanded) && expanded.length === 1 ? expanded[0] : expanded;
    const processed = await processObject(jsonld, doc, maxDepth, currentDepth + 1, visited);
    return processed;
  } catch (error) {
    return { "@id": url, "_error": error.message };
  }
}

async function processObject(jsonld, obj, maxDepth, currentDepth, visited) {
  if (Array.isArray(obj)) {
    const processed = await Promise.all(
      obj.map(item => processObject(jsonld, item, maxDepth, currentDepth, visited))
    );
    return processed.length === 1 ? processed[0] : processed;
  }
  
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  const keys = Object.keys(obj);
  
<<<<<<< HEAD
  // Expand any @id reference (http://, https://, or file://)
  if (keys.length === 1 && keys[0] === '@id' && typeof obj['@id'] === 'string' && 
      (obj['@id'].startsWith('http') || obj['@id'].startsWith('file://')) && 
      currentDepth < maxDepth) {
=======
  if (keys.length === 1 && keys[0] === '@id' && typeof obj['@id'] === 'string' && 
      obj['@id'].startsWith('http') && currentDepth < maxDepth) {
>>>>>>> 7e7799a (v1 no local files)
    return await expandRecursive(jsonld, obj['@id'], maxDepth, currentDepth, visited);
  }
  
  const result = {};
  for (const [key, value] of Object.entries(obj)) {
    if (Array.isArray(value)) {
      const processed = await Promise.all(
        value.map(item => processObject(jsonld, item, maxDepth, currentDepth, visited))
      );
      result[key] = processed.length === 1 ? processed[0] : processed;
    } else if (value && typeof value === 'object') {
      result[key] = await processObject(jsonld, value, maxDepth, currentDepth, visited);
    } else {
      result[key] = value;
    }
  }
  return result;
}

async function compactJsonLd(jsonld, url, depth = 2) {
<<<<<<< HEAD
  // Expand recursively
  const expanded = await expandRecursive(jsonld, url, depth);
  
  // Compact using the original URL as context
  // jsonld will load it and extract @context, then resolve relative contexts automatically!
  const compacted = await jsonld.compact(expanded, url);
  
=======
  // First, expand the document recursively
  const expanded = await expandRecursive(jsonld, url, depth);
  
  // Fetch the original document to extract its context
  let context = url;
  
  try {
    // Load the original document
    const response = await jsonld.documentLoader(url);
    const originalDoc = response.document;
    
    // If the document has a @context, use it
    if (originalDoc && originalDoc['@context']) {
      context = originalDoc['@context'];
    }
  } catch (error) {
    console.warn('Could not fetch context from URL, using URL as context:', error.message);
  }
  
  // Compact the expanded document with the proper context
  const compacted = await jsonld.compact(expanded, context);
  
  // Return the graph if present, otherwise return the compacted doc
>>>>>>> 7e7799a (v1 no local files)
  return compacted["@graph"] ?? compacted;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { expandRecursive, compactJsonLd, processObject };
} else if (typeof window !== 'undefined') {
  window.LdrCore = { expandRecursive, compactJsonLd, processObject };
}
