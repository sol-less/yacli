#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MAIN_FILE = PROJECT_ROOT / "yacli" / "main.py"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

def clean():
    """Removes previous build artifacts."""
    print("[*] Cleaning build directory...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

def build():
    """Compiles yacli into a single binary executable."""
    clean()
    print("[*] Compiling yacli into a standalone binary...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=yacli",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}",
        str(MAIN_FILE)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n[+] Build successful!")
        print(f"[+] Binary output: {DIST_DIR / 'yacli'}")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Build failed with error code {e.returncode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build()
