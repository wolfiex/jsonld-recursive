#!/usr/bin/env node
/**
 * LDR Server - Standalone version for Python package
 * This file is bundled with the Python package and requires ldr-core.js in the same directory.
 */

process.title = 'ldr-server';

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Try to load jsonld from multiple locations
let jsonld;
const jsonldPaths = [
  'jsonld',  // Normal require (global or local node_modules)
  path.join(__dirname, 'node_modules', 'jsonld'),
  path.join(__dirname, '..', 'node_modules', 'jsonld'),
  path.join(process.cwd(), 'node_modules', 'jsonld'),
  '/usr/local/lib/node_modules/jsonld',
  '/usr/lib/node_modules/jsonld',
  path.join(process.env.HOME || '', '.npm-global', 'lib', 'node_modules', 'jsonld'),
  path.join(process.env.HOME || '', 'node_modules', 'jsonld'),
];

for (const p of jsonldPaths) {
  try {
    jsonld = require(p);
    console.log(`Loaded jsonld from: ${p}`);
    break;
  } catch (e) {
    // Try next path
  }
}

if (!jsonld) {
  console.error('ERROR: jsonld package not found.');
  console.error('Tried paths:', jsonldPaths);
  console.error('');
  console.error('Install it with one of:');
  console.error('  npm install -g jsonld');
  console.error('  npm install jsonld');
  console.error('  cd ' + __dirname + ' && npm install jsonld');
  process.exit(1);
}

// Load ldr-core from same directory
const { expandRecursive, compactJsonLd } = require('./ldr-core.js');

// In-memory cache and mappings
const cache = new Map();
let urlMappings = {};

// Apply URL mappings with wildcard support and chaining
function applyMappings(url, maxDepth = 10) {
  let currentUrl = url;
  let depth = 0;
  
  while (depth < maxDepth) {
    const nextUrl = applySingleMapping(currentUrl);
    if (nextUrl === currentUrl) break;
    currentUrl = nextUrl;
    depth++;
  }
  
  if (depth >= maxDepth) {
    console.warn(`Max mapping depth (${maxDepth}) reached for ${url}`);
  }
  
  return currentUrl;
}

function applySingleMapping(url) {
  if (urlMappings[url]) return urlMappings[url];
  
  for (const [pattern, replacement] of Object.entries(urlMappings)) {
    if (pattern.includes('*')) {
      const regexPattern = pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '(.*)');
      const regex = new RegExp('^' + regexPattern + '$');
      const match = url.match(regex);
      
      if (match) {
        let result = replacement;
        result = result.replace(/\$\{rest\}/g, match[1] || '');
        for (let i = 0; i < match.length; i++) {
          result = result.replace(new RegExp(`\\$${i}`, 'g'), match[i] || '');
        }
        return result;
      }
    }
  }
  
  return url;
}

// Custom document loader
async function documentLoader(url) {
  const resolvedUrl = applyMappings(url);
  
  if (resolvedUrl !== url) {
    console.log(`Mapping: ${url} -> ${resolvedUrl}`);
  }
  
  // Local file path
  if (!resolvedUrl.startsWith('http://') && !resolvedUrl.startsWith('https://')) {
    try {
      const absolutePath = path.resolve(resolvedUrl.replace('file://', ''));
      const content = fs.readFileSync(absolutePath, 'utf8');
      const document = JSON.parse(content);
      
      console.log(`Loaded local: ${absolutePath}`);
      
      return {
        contextUrl: null,
        document: document,
        documentUrl: 'file://' + absolutePath
      };
    } catch (error) {
      throw new Error(`Could not load local file ${resolvedUrl}: ${error.message}`);
    }
  }
  
  // HTTP/HTTPS URLs
  return new Promise((resolve, reject) => {
    const client = resolvedUrl.startsWith('https:') ? https : http;
    
    client.get(resolvedUrl, { headers: { 'Accept': 'application/ld+json, application/json' } }, (res) => {
      let data = '';
      
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
          if (Array.isArray(document)) {
            document = { '@context': document };
          }
          resolve({ contextUrl: null, document: document, documentUrl: resolvedUrl });
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
    if (url.pathname === '/health' && req.method === 'GET') {
      sendJson(res, 200, { status: 'ok', cache_size: cache.size, mappings_count: Object.keys(urlMappings).length });
      return;
    }

    if (url.pathname === '/mappings' && req.method === 'GET') {
      sendJson(res, 200, { mappings: urlMappings });
      return;
    }

    if (url.pathname === '/mappings' && req.method === 'POST') {
      const body = await parseBody(req);
      if (body.file) {
        try {
          urlMappings = JSON.parse(fs.readFileSync(body.file, 'utf8'));
          sendJson(res, 200, { message: 'Mappings loaded', count: Object.keys(urlMappings).length, mappings: urlMappings });
        } catch (error) {
          sendJson(res, 400, { error: `Failed to load mappings: ${error.message}` });
        }
      } else if (body.mappings) {
        urlMappings = body.mappings;
        sendJson(res, 200, { message: 'Mappings set', count: Object.keys(urlMappings).length, mappings: urlMappings });
      } else {
        sendJson(res, 400, { error: 'Missing file or mappings' });
      }
      return;
    }

    if (url.pathname === '/mappings' && req.method === 'DELETE') {
      const count = Object.keys(urlMappings).length;
      urlMappings = {};
      sendJson(res, 200, { cleared: count });
      return;
    }

    if (url.pathname === '/cache/stats' && req.method === 'GET') {
      sendJson(res, 200, { size: cache.size, keys: Array.from(cache.keys()) });
      return;
    }

    if (url.pathname === '/cache/list' && req.method === 'GET') {
      sendJson(res, 200, { count: cache.size, urls: Array.from(cache.keys()) });
      return;
    }

    if (url.pathname === '/cache' && req.method === 'DELETE') {
      const size = cache.size;
      cache.clear();
      sendJson(res, 200, { cleared: size });
      return;
    }

    if (url.pathname === '/expand' && req.method === 'POST') {
      const body = await parseBody(req);
      if (!body.url) { sendJson(res, 400, { error: 'Missing url' }); return; }

      const depth = body.depth || 2;
      const cacheKey = getCacheKey(body.url, depth, 'expand');
      
      if (cache.has(cacheKey)) {
        console.log(`Cache HIT: ${cacheKey}`);
        sendJson(res, 200, { result: cache.get(cacheKey), cached: true });
        return;
      }

      console.log(`Cache MISS: ${cacheKey}`);
      const result = await expandRecursive(jsonld, body.url, depth);
      cache.set(cacheKey, result);
      sendJson(res, 200, { result, cached: false });
      return;
    }

    if (url.pathname === '/compact' && req.method === 'POST') {
      const body = await parseBody(req);
      if (!body.url) { sendJson(res, 400, { error: 'Missing url' }); return; }

      const depth = body.depth || 2;
      const cacheKey = getCacheKey(body.url, depth, 'compact');
      
      if (cache.has(cacheKey)) {
        console.log(`Cache HIT: ${cacheKey}`);
        sendJson(res, 200, { result: cache.get(cacheKey), cached: true });
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
const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`LDR Server running on http://localhost:${PORT}`);
  console.log(`Stop with: pkill ldr-server`);
});

process.on('SIGTERM', () => { cache.clear(); server.close(() => process.exit(0)); });
process.on('SIGINT', () => { cache.clear(); server.close(() => process.exit(0)); });
