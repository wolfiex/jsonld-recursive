#!/usr/bin/env python3
"""
LDR (JSON-LD Recursive) Python Client Library
"""

import requests
import json
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class LdrClient:
    """
    Client for LDR Server API.
    
    Supports auto-starting server and connection pooling.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:3000",
        timeout: int = 30,
        max_retries: int = 3,
        auto_start_server: bool = False,
        mappings_file: Optional[str] = None
    ):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the LDR server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            auto_start_server: Automatically start server if not running
            mappings_file: Path to JSON file with URL mappings
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auto_started = False
        self.server_pid = None
        self.mappings_file = mappings_file
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Auto-start server if requested
        if auto_start_server:
            if not self._is_server_running():
                self._start_server()
    
    def _is_server_running(self) -> bool:
        """Check if server is running."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _find_server_script(self) -> Optional[str]:
        """Find ldr-server.js script."""
        # Current directory
        if os.path.exists('ldr-server.js'):
            return os.path.abspath('ldr-server.js')
        
        # Parent directory
        if os.path.exists('../ldr-server.js'):
            return os.path.abspath('../ldr-server.js')
        
        # node_modules
        paths = [
            'node_modules/jsonld-recursive/ldr-server.js',
            '../node_modules/jsonld-recursive/ldr-server.js'
        ]
        for p in paths:
            if os.path.exists(p):
                return os.path.abspath(p)
        
        return None
    
    def _start_server(self, port: int = 3000):
        """Start the server in background."""
        server_script = self._find_server_script()
        
        if not server_script:
            raise RuntimeError(
                "Could not find ldr-server.js. "
                "Install with: npm install jsonld-recursive"
            )
        
        print(f"Starting LDR server on port {port}...", flush=True)
        
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        if self.mappings_file:
            env['MAPPINGS_FILE'] = self.mappings_file
        
        self.server_process = subprocess.Popen(
            ['node', server_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True
        )
        
        self.server_pid = self.server_process.pid
        self.auto_started = True
        
        # Wait for server to start
        for i in range(20):
            time.sleep(0.5)
            if self._is_server_running():
                print(f"Server started (PID: {self.server_pid})", flush=True)
                return
        
        raise RuntimeError("Server failed to start within 10 seconds")
    
    def stop_server(self):
        """Stop auto-started server."""
        if not self.auto_started:
            return
        
        try:
            subprocess.run(['pkill', 'ldr-server'], timeout=2)
            print(f"Server stopped", flush=True)
            self.auto_started = False
        except Exception as e:
            print(f"Failed to stop server: {e}", flush=True)
    
    def set_mappings(self, mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Set URL mappings.
        
        Args:
            mappings: Dictionary of URL mappings {original: replacement}
            
        Example:
            >>> client.set_mappings({
            ...     "https://old.com/data": "https://new.com/data"
            ... })
        """
        response = self.session.post(
            f"{self.base_url}/mappings",
            json={"mappings": mappings},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def load_mappings(self, file_path: str) -> Dict[str, Any]:
        """
        Load URL mappings from file.
        
        Args:
            file_path: Path to JSON file with mappings
            
        Example:
            >>> client.load_mappings("mappings.json")
        """
        response = self.session.post(
            f"{self.base_url}/mappings",
            json={"file": file_path},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_mappings(self) -> Dict[str, str]:
        """Get current URL mappings."""
        response = self.session.get(
            f"{self.base_url}/mappings",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['mappings']
    
    def clear_mappings(self) -> int:
        """Clear URL mappings."""
        response = self.session.delete(
            f"{self.base_url}/mappings",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['cleared']
    
    def health(self) -> Dict[str, Any]:
        """Check server health."""
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def expand(
        self, 
        url: str, 
        depth: int = 2,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """Expand a JSON-LD document recursively."""
        response = self.session.post(
            f"{self.base_url}/expand",
            json={"url": url, "depth": depth},
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        if verbose:
            if data.get('cached'):
                print(f"[Cache HIT] {url} (depth={depth})", flush=True)
            else:
                print(f"[Cache MISS] {url} (depth={depth})", flush=True)
            
        return data['result']
    
    def compact(
        self, 
        url: str, 
        depth: int = 2,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """Expand and compact a JSON-LD document recursively."""
        response = self.session.post(
            f"{self.base_url}/compact",
            json={"url": url, "depth": depth},
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        if verbose:
            if data.get('cached'):
                print(f"[Cache HIT] {url} (depth={depth})", flush=True)
            else:
                print(f"[Cache MISS] {url} (depth={depth})", flush=True)
            
        return data['result']
    
    def compact_batch(
        self,
        urls: List[str],
        depth: int = 2,
        verbose: bool = True
    ) -> List[Dict[str, Any]]:
        """Compact multiple URLs."""
        results = []
        for i, url in enumerate(urls):
            if verbose:
                print(f"Processing {i+1}/{len(urls)}: {url}")
            result = self.compact(url, depth, verbose=verbose)
            results.append(result)
        return results
    
    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        response = self.session.get(
            f"{self.base_url}/cache/stats",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def cache_list(self) -> Dict[str, Any]:
        """List cached URLs."""
        response = self.session.get(
            f"{self.base_url}/cache/list",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def cache_clear(self) -> int:
        """Clear the cache."""
        response = self.session.delete(
            f"{self.base_url}/cache",
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        cleared = data['cleared']
        print(f"Cache cleared: {cleared} entries removed", flush=True)
        return cleared
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.auto_started:
            self.stop_server()
        self.close()
    
    def __del__(self):
        """Destructor."""
        try:
            self.close()
        except:
            pass
