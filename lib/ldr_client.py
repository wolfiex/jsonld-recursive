#!/usr/bin/env python3
"""
LDR (JSON-LD Recursive) Python Client Library
"""

import requests
import json
import subprocess
import time
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional


class LdrClient:
    """
    Client for LDR Server API.
    
    Supports auto-starting server and connection pooling.
    """
    
    DEFAULT_PORT = 3333
    MAX_PORT_ATTEMPTS = 10
    
    def __init__(
        self, 
        base_url: str = None,
        timeout: int = 30,
        max_retries: int = 3,
        auto_start_server: bool = False,
        mappings_file: Optional[str] = None,
        mappings: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the LDR server (default: http://localhost:3333)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            auto_start_server: Automatically start server if not running
            mappings_file: Path to JSON file with URL mappings
            mappings: Dictionary of URL mappings to set on initialization
        """
        self.base_url = (base_url or f"http://localhost:{self.DEFAULT_PORT}").rstrip('/')
        self.timeout = timeout
        self.auto_started = False
        self.server_pid = None
        self.server_process = None
        self.mappings_file = mappings_file
        self.initial_mappings = mappings
        self.port = self._extract_port(self.base_url)
        
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
            
            # Set mappings after server starts
            if self.initial_mappings:
                time.sleep(0.5)  # Give server a moment to fully start
                self.set_mappings(self.initial_mappings)
    
    def _is_server_running(self, port: int = None) -> bool:
        """Check if server is running on specified port."""
        if port is None:
            port = self.port
        try:
            response = self.session.get(f"http://localhost:{port}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _extract_port(self, url: str) -> int:
        """Extract port number from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.port or self.DEFAULT_PORT
        except:
            return self.DEFAULT_PORT
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def _find_available_port(self, start_port: int = None) -> int:
        """Find an available port starting from start_port."""
        if start_port is None:
            start_port = self.DEFAULT_PORT
        
        for i in range(self.MAX_PORT_ATTEMPTS):
            port = start_port + i
            if not self._is_port_in_use(port):
                return port
        
        raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + self.MAX_PORT_ATTEMPTS}")
    
    def _ensure_jsonld_installed(self, server_script_dir: str) -> bool:
        """Ensure jsonld npm package is installed. Returns True if available."""
        # Check if jsonld is available globally or locally
        check_script = '''
        try {
          require('jsonld');
          process.exit(0);
        } catch(e) {
          process.exit(1);
        }
        '''
        result = subprocess.run(
            ['node', '-e', check_script],
            capture_output=True,
            cwd=server_script_dir
        )
        
        if result.returncode == 0:
            return True
        
        # Try to install jsonld in the server script directory
        print("Installing jsonld npm package...", flush=True)
        
        # Check if package.json exists, if not create a minimal one
        package_json = Path(server_script_dir) / 'package.json'
        if not package_json.exists():
            with open(package_json, 'w') as f:
                f.write('{"name":"ldr-server-deps","dependencies":{"jsonld":"^8.3.1"}}')
        
        # Run npm install
        result = subprocess.run(
            ['npm', 'install', '--silent'],
            capture_output=True,
            text=True,
            cwd=server_script_dir
        )
        
        if result.returncode != 0:
            print(f"Warning: Failed to install jsonld: {result.stderr}", flush=True)
            print("Please install manually: npm install -g jsonld", flush=True)
            return False
        
        print("jsonld installed successfully", flush=True)
        return True
    
    def _start_server(self, port: int = None):
        """Start the server in background, finding an available port if needed."""
        # First check if server is already running on default port
        if self._is_server_running(self.DEFAULT_PORT):
            self.port = self.DEFAULT_PORT
            self.base_url = f"http://localhost:{self.port}"
            print(f"Using existing server on port {self.port}", flush=True)
            return
        
        # Find an available port
        if port is None:
            port = self._find_available_port(self.DEFAULT_PORT)
        
        self.port = port
        self.base_url = f"http://localhost:{self.port}"
        
        # Find the server script first (preferred method - more reliable)
        server_script = self._find_server_script()
        
        if server_script:
            server_script_dir = str(Path(server_script).parent)
            
            # Check if Node.js is available
            if not shutil.which('node'):
                raise RuntimeError(
                    "Node.js is required to run the server. "
                    "Install Node.js from https://nodejs.org/"
                )
            
            # Ensure jsonld is installed
            self._ensure_jsonld_installed(server_script_dir)
            
            print(f"Starting LDR server on port {port}...", flush=True)
            
            env = os.environ.copy()
            env['PORT'] = str(port)
            
            if self.mappings_file:
                env['MAPPINGS_FILE'] = self.mappings_file
            
            # Set NODE_PATH to help find jsonld module
            node_paths = [
                os.path.join(server_script_dir, 'node_modules'),  # Local to script
                '/usr/local/lib/node_modules',
                '/usr/lib/node_modules',
                os.path.expanduser('~/.npm-global/lib/node_modules'),
                os.path.expanduser('~/node_modules'),
                './node_modules',
            ]
            existing_node_path = env.get('NODE_PATH', '')
            if existing_node_path:
                node_paths.insert(0, existing_node_path)
            env['NODE_PATH'] = os.pathsep.join(node_paths)
            
            # Start server in background with Popen
            self.server_process = subprocess.Popen(
                ['node', server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                start_new_session=True
            )
            
            self.server_pid = self.server_process.pid
            self.auto_started = True
            
            # Wait for server to start, checking for early failure
            for i in range(20):
                time.sleep(0.5)
                
                # Check if process died
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    error_msg = stderr.decode() if stderr else stdout.decode()
                    if 'jsonld' in error_msg.lower():
                        raise RuntimeError(
                            f"Server failed - jsonld npm package not found.\n"
                            f"Install it with: npm install -g jsonld\n"
                            f"Error: {error_msg}"
                        )
                    raise RuntimeError(f"Server process died: {error_msg}")
                
                if self._is_server_running():
                    print(f"Server started (PID: {self.server_pid})", flush=True)
                    return
            
            raise RuntimeError("Server failed to start within 10 seconds")
        
        # Fallback: try global ldr command
        if shutil.which('ldr'):
            print(f"Starting LDR server on port {port} (using global ldr command)...", flush=True)
            
            # Use Popen instead of run to avoid blocking
            cmd = ['ldr', 'server', 'start', str(port)]
            if self.mappings_file:
                cmd.append(self.mappings_file)
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            self.auto_started = True
            
            for i in range(20):
                time.sleep(0.5)
                if self._is_server_running():
                    print(f"Server started on port {port}", flush=True)
                    return
            
            raise RuntimeError("Server failed to start within 10 seconds")
        
        raise RuntimeError(
            "Could not find ldr-server.js or ldr command. "
            "Install with: npm install -g jsonld-recursive"
        )
    
    def _find_server_script(self) -> Optional[str]:
        """Find ldr-server.js script."""
        # First check: same directory as this Python file (installed package)
        package_dir = Path(__file__).parent
        server_script = package_dir / 'ldr-server.js'
        if server_script.exists():
            return str(server_script.absolute())
        
        # Current directory
        if os.path.exists('ldr-server.js'):
            return os.path.abspath('ldr-server.js')
        
        # Parent directory
        if os.path.exists('../ldr-server.js'):
            return os.path.abspath('../ldr-server.js')
        
        # Parent of package directory (for editable installs)
        server_script = package_dir.parent / 'ldr-server.js'
        if server_script.exists():
            return str(server_script.absolute())
        
        # node_modules
        paths = [
            'node_modules/jsonld-recursive/ldr-server.js',
            '../node_modules/jsonld-recursive/ldr-server.js'
        ]
        for p in paths:
            if os.path.exists(p):
                return os.path.abspath(p)
        
        return None
    
    def stop_server(self):
        """Stop auto-started server."""
        if not self.auto_started:
            return
        
        try:
            # Use ldr command if available
            if shutil.which('ldr'):
                subprocess.run(['ldr', 'server', 'stop'], timeout=2, capture_output=True)
            else:
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
