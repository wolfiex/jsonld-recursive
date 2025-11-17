// ldr-browser.js
// Browser wrapper for ldr-core

(function(global) {
  'use strict';

  async function ensureJsonLd() {
    if (typeof jsonld !== 'undefined') {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/jsonld@8.3.1/dist/jsonld.min.js';
      script.onload = resolve;
      script.onerror = () => reject(new Error('Failed to load jsonld.js'));
      document.head.appendChild(script);
    });
  }

  function setupDocumentLoader() {
    const customLoader = async (url) => {
      // Check for local file paths
      if (url.startsWith('file://') || (url.startsWith('/') && !url.startsWith('http'))) {
        throw new Error(
          `Cannot load local file "${url}" in browser. ` +
          `Browsers cannot access local files due to security restrictions. ` +
          `Please use the server version (ldr-server.js) with mappings to handle local files, ` +
          `or serve the file over HTTP.`
        );
      }
      
      try {
        const response = await fetch(url, {
          headers: { 'Accept': 'application/ld+json, application/json' }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const document = await response.json();
        
        return {
          contextUrl: null,
          document: document,
          documentUrl: url
        };
      } catch (error) {
        if (error.message.includes('Failed to fetch')) {
          throw new Error(
            `Failed to fetch "${url}". This could be due to:\n` +
            `1. CORS restrictions (server must allow cross-origin requests)\n` +
            `2. Network connectivity issues\n` +
            `3. Invalid URL\n` +
            `Original error: ${error.message}`
          );
        }
        throw error;
      }
    };
    
    jsonld.documentLoader = customLoader;
  }

  const JsonLdExpand = {
    async init() {
      await ensureJsonLd();
      setupDocumentLoader();
      return this;
    },

    async expand(url, options = {}) {
      await ensureJsonLd();
      setupDocumentLoader();
      
      const { depth = 2 } = options;
      return await window.LdrCore.expandRecursive(jsonld, url, depth);
    },

    async compact(url, options = {}) {
      await ensureJsonLd();
      setupDocumentLoader();
      
      const { depth = 2 } = options;
      return await window.LdrCore.compactJsonLd(jsonld, url, depth);
    }
  };

  global.JsonLdExpand = JsonLdExpand;

})(typeof window !== 'undefined' ? window : global);
