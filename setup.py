#!/usr/bin/env python3
"""
Custom setup.py to run post-install verification tests.
The install will FAIL if tests don't pass.
"""

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess
import sys


class PostInstallTest:
    """Mixin to run tests after install."""
    
    def run_tests(self):
        """Run the installation verification tests including server test."""
        print("\n" + "=" * 60)
        print("Running post-install verification tests...")
        print("=" * 60 + "\n")
        
        # Run the full test with auto-start server
        result = subprocess.run(
            [sys.executable, "-c", """
from jsonld_recursive.test_install import test_local_files, test_client_with_local_files
import sys

# Test 1: Basic file tests
print("Step 1/2: Testing bundled files...")
if not test_local_files():
    print("FAILED: Bundled test files are missing or invalid")
    sys.exit(1)

print()

# Test 2: Server + local files test
print("Step 2/2: Testing server with local files...")
if not test_client_with_local_files(auto_start=True):
    print("FAILED: Server test with local files failed")
    sys.exit(1)

print()
print("All tests passed!")
sys.exit(0)
"""],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            print("\n" + "=" * 60)
            print("ERROR: Post-install tests FAILED!")
            print("The package may not be installed correctly.")
            print("=" * 60 + "\n")
            raise SystemExit("Installation verification failed")
        
        print("\n" + "=" * 60)
        print("✓ Post-install tests PASSED (including server test)")
        print("=" * 60 + "\n")


class InstallWithTest(install, PostInstallTest):
    """Custom install command that runs tests after installation."""
    
    def run(self):
        install.run(self)
        self.run_tests()


class DevelopWithTest(develop, PostInstallTest):
    """Custom develop command that runs tests after installation."""
    
    def run(self):
        develop.run(self)
        self.run_tests()


setup(
    cmdclass={
        'install': InstallWithTest,
        'develop': DevelopWithTest,
    }
)
