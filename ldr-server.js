#!/usr/bin/env node

process.title = 'ldr-server';

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const jsonld = require('jsonld');
const { expandRecursive, compactJsonLd } = require('./lib/ldr-core');

// In-memory cache and mappings
const cache = new Map();
let urlMappings = {};

// Apply URL mappings with wildcard support and chaining
function applyMappings(url, maxDepth = 10) {
  let currentUrl = url;
  let depth = 0;
  
  while (depth < maxDepth) {
    const nextUrl = applySingleMapping(currentUrl);
    
    // No change - we're done
    if (nextUrl === currentUrl) {
      break;
    }
    
    currentUrl = nextUrl;
    depth++;
  }
  
  if (depth >= maxDepth) {
    console.warn(`Max mapping depth (${maxDepth}) reached for ${url}`);
  }
  
  return currentUrl;
}

function applySingleMapping(url) {
  // Direct match
  if (urlMappings[url]) {
    return urlMappings[url];
  }
  
  // Wildcard match
  for (const [pattern, replacement] of Object.entries(urlMappings)) {
    if (pattern.includes('*')) {
      const regexPattern = pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '(.*)');
      const regex = new RegExp('^' + regexPattern + '$');
      const match = url.match(regex);
      
      if (match) {
        let result = replacement;
        // Replace ${rest} with captured group
        result = result.replace(/\$\{rest\}/g, match[1] || '');
        // Also support $1, $2, etc.
        for (let i = 0; i < match.length; i++) {
          result = result.replace(new RegExp(`\\$${i}`, 'g'), match[i] || '');
        }
        return result;
      }
    }
  }
  
  return url;
}

// Custom document loader - treats local files as file:// URLs
async function documentLoader(url) {
  // Apply chained mappings first
  const resolvedUrl = applyMappings(url);
  
  if (resolvedUrl !== url) {
    console.log(`Mapping: ${url} -> ${resolvedUrl}`);
  }
  
  // Check if it's a local file path (NOT http:// or https://)
  if (!resolvedUrl.startsWith('http://') && !resolvedUrl.startsWith('https://')) {
    try {
      // Resolve to absolute path
      const absolutePath = path.resolve(resolvedUrl.replace('file://', ''));
      const content = fs.readFileSync(absolutePath, 'utf8');
      const document = JSON.parse(content);
      
      console.log(`Loaded local: ${absolutePath}`);
      
      // Return with file:// URL - jsonld uses this to resolve relative @context paths!
      return {
        contextUrl: null,
        document: document,
        documentUrl: 'file://' + absolutePath
      };
    } catch (error) {
      throw new Error(`Could not load local file ${resolvedUrl}: ${error.message}`);
    }
  }
  
  // Handle http/https URLs
  return new Promise((resolve, reject) => {
    const client = resolvedUrl.startsWith('https:') ? https : http;
    
    client.get(resolvedUrl, { headers: { 'Accept': 'application/ld+json, application/json' } }, (res) => {
      let data = '';
      
      // Handle redirects
      if (res.statusCode === 301 || res.statusCode === 302) {
        return documentLoader(res.headers.location).then(resolve).catch(reject);
      }
      
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
        return;
      }
      
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          let document = JSON.parse(data);
          
          // Handle array context
          if (Array.isArray(document)) {
            document = { '@context': document };
          }
          
          resolve({
            contextUrl: null,
            document: document,
            documentUrl: resolvedUrl
          });
        } catch (error) {
          reject(new Error(`Failed to parse JSON from ${resolvedUrl}: ${error.message}`));
        }
      });
    }).on('error', reject);
  });
}

jsonld.documentLoader = documentLoader;

function getCacheKey(url, depth, operation) {
  return `${operation}:${url}:${depth}`;
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(new Error('Invalid JSON'));
      }
    });
  });
}

function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(JSON.stringify(data, null, 2));
}

async function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  try {
    // Health
    if (url.pathname === '/health' && req.method === 'GET') {
      sendJson(res, 200, { 
        status: 'ok',
        cache_size: cache.size,
        mappings_count: Object.keys(urlMappings).length
      });
      return;
    }

    // Get mappings
    if (url.pathname === '/mappings' && req.method === 'GET') {
      sendJson(res, 200, { mappings: urlMappings });
      return;
    }

    // Set mappings
    if (url.pathname === '/mappings' && req.method === 'POST') {
      const body = await parseBody(req);
      
      if (body.file) {
        try {
          const fileContent = fs.readFileSync(body.file, 'utf8');
          urlMappings = JSON.parse(fileContent);
          console.log(`Loaded ${Object.keys(urlMappings).length} mappings from ${body.file}`);
          sendJson(res, 200, { 
            message: 'Mappings loaded from file',
            count: Object.keys(urlMappings).length,
            mappings: urlMappings
          });
        } catch (error) {
          sendJson(res, 400, { error: `Failed to load mappings: ${error.message}` });
        }
      } else if (body.mappings) {
        urlMappings = body.mappings;
        console.log(`Set ${Object.keys(urlMappings).length} mappings`);
        sendJson(res, 200, { 
          message: 'Mappings set',
          count: Object.keys(urlMappings).length,
          mappings: urlMappings
        });
      } else {
        sendJson(res, 400, { error: 'Missing file or mappings' });
      }
      return;
    }

    // Clear mappings
    if (url.pathname === '/mappings' && req.method === 'DELETE') {
      const count = Object.keys(urlMappings).length;
      urlMappings = {};
      console.log('Mappings cleared');
      sendJson(res, 200, { cleared: count });
      return;
    }

    // Cache stats
    if (url.pathname === '/cache/stats' && req.method === 'GET') {
      sendJson(res, 200, { 
        size: cache.size,
        keys: Array.from(cache.keys())
      });
      return;
    }

    // Cache list
    if (url.pathname === '/cache/list' && req.method === 'GET') {
      const urls = Array.from(cache.keys());
      sendJson(res, 200, { count: urls.length, urls: urls });
      return;
    }

    // Clear cache
    if (url.pathname === '/cache' && req.method === 'DELETE') {
      const size = cache.size;
      cache.clear();
      console.log(`Cache cleared: ${size} entries removed`);
      sendJson(res, 200, { cleared: size });
      return;
    }

    // Expand
    if (url.pathname === '/expand' && req.method === 'POST') {
      const body = await parseBody(req);
      
      if (!body.url) {
        sendJson(res, 400, { error: 'Missing url' });
        return;
      }

      const depth = body.depth || 2;
      const cacheKey = getCacheKey(body.url, depth, 'expand');
      
      if (cache.has(cacheKey)) {
        console.log(`Cache HIT: ${cacheKey}`);
        sendJson(res, 200, { 
          result: cache.get(cacheKey),
          cached: true 
        });
        return;
      }

      console.log(`Cache MISS: ${cacheKey}`);
      const result = await expandRecursive(jsonld, body.url, depth);
      cache.set(cacheKey, result);
      
      sendJson(res, 200, { result, cached: false });
      return;
    }

    // Compact
    if (url.pathname === '/compact' && req.method === 'POST') {
      const body = await parseBody(req);
      
      if (!body.url) {
        sendJson(res, 400, { error: 'Missing url' });
        return;
      }

      const depth = body.depth || 2;
      const cacheKey = getCacheKey(body.url, depth, 'compact');
      
      if (cache.has(cacheKey)) {
        console.log(`Cache HIT: ${cacheKey}`);
        sendJson(res, 200, { 
          result: cache.get(cacheKey),
          cached: true 
        });
        return;
      }

      console.log(`Cache MISS: ${cacheKey}`);
      const result = await compactJsonLd(jsonld, body.url, depth);
      cache.set(cacheKey, result);
      
      sendJson(res, 200, { result, cached: false });
      return;
    }

    sendJson(res, 404, { error: 'Not found' });
  } catch (error) {
    console.error('Error:', error);
    sendJson(res, 500, { error: error.message });
  }
}

const PORT = process.env.PORT || 3000;
const MAPPINGS_FILE = process.env.MAPPINGS_FILE;

const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`LDR Server (ldr-server) running on http://localhost:${PORT}`);
  console.log(`Process title: ${process.title}`);
  console.log(`Stop with: pkill ldr-server`);
  console.log('');
  console.log('Endpoints:');
  console.log('  POST /expand         - Expand JSON-LD');
  console.log('  POST /compact        - Compact JSON-LD');
  console.log('  GET  /health         - Health check');
  console.log('  GET  /cache/stats    - Cache statistics');
  console.log('  DELETE /cache        - Clear cache');
  console.log('  GET  /mappings       - Get URL mappings');
  console.log('  POST /mappings       - Set URL mappings');
  console.log('  DELETE /mappings     - Clear mappings');
  console.log('');
  console.log('Features:');
  console.log('  ✓ HTTP/HTTPS URLs');
  console.log('  ✓ Local file paths (absolute and relative)');
  console.log('  ✓ Automatic relative @context resolution via file:// URLs');
  console.log('  ✓ Chained URL mappings');
  console.log('');
  
  // Load mappings from file if specified
  if (MAPPINGS_FILE) {
    try {
      const fileContent = fs.readFileSync(MAPPINGS_FILE, 'utf8');
      urlMappings = JSON.parse(fileContent);
      console.log(`Loaded ${Object.keys(urlMappings).length} URL mappings from ${MAPPINGS_FILE}`);
      console.log('Mapping examples:');
      Object.entries(urlMappings).slice(0, 3).forEach(([k, v]) => {
        console.log(`  ${k} -> ${v}`);
      });
    } catch (error) {
      console.error(`Failed to load mappings from ${MAPPINGS_FILE}: ${error.message}`);
    }
  }
  
  console.log(`Cache: ${cache.size} entries`);
  console.log(`Mappings: ${Object.keys(urlMappings).length} rules`);
});

// Clear cache on exit
process.on('SIGTERM', () => {
  console.log('\nSIGTERM received, clearing cache...');
  cache.clear();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, clearing cache...');
  cache.clear();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
