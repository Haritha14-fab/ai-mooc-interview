#!/usr/bin/env python
"""
Backend server startup script
"""
import os
import sys
import subprocess

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add backend to path
sys.path.insert(0, backend_dir)

# Run uvicorn
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--port", "8001",
    "--host", "127.0.0.1"
])
