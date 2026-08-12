import os
import subprocess
import sys
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "quickshell"

def handle_build(config_dir: Path, verbose: bool, quiet: bool):
    if not quiet:
        print("[*] Building Y3s modules...")
    try:
        stdout = None if verbose else subprocess.DEVNULL
        stderr = None if verbose else subprocess.PIPE
        subprocess.run(["cmake", "-B", "build"], cwd=config_dir, check=True, stdout=stdout, stderr=stderr)
        if not quiet:
            print("[+] Build complete!")
    except subprocess.CalledProcessError as e:
        print(f"[-] Build failed: {e}", file=sys.stderr)

def handle_run(config_dir: Path, config_file: str, verbose: bool, quiet: bool):
    if not quiet:
        print("[*] Launching yamd3s in background...")

    env = os.environ.copy()
    build_dir = str(config_dir / "build")
    env["QML2_IMPORT_PATH"] = build_dir
    env["QML_IMPORT_PATH"] = build_dir

    cmd = ["quickshell"]
    if config_file:
        cmd.extend(["-c", config_file])

    try:
        subprocess.Popen(
            cmd, 
            cwd=config_dir, 
            env=env, 
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None,
            start_new_session=True
        )
        if not quiet:
            print("[+] Quickshell started!")
    except Exception as e:
        print(f"[-] Failed to start quickshell: {e}", file=sys.stderr)

def handle_kill(quiet: bool):
    if not quiet:
        print("[*] Stopping quickshell...")
    subprocess.run(["pkill", "-x", "quickshell"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def handle_list(config_dir: Path):
    build_dir = config_dir / "build" / "Y3s"
    print("[+] Available Y3s Modules:")
    if not build_dir.exists():
        print("    (No modules built yet. Run 'yacli shell build' first.)")
        return
    for module in build_dir.iterdir():
        if module.is_dir():
            print(f"    -> Y3s.{module.name}")

def handle_ipc_list():
    print("[*] Querying active Quickshell IPC endpoints...\n")
    try:
        subprocess.run(["quickshell", "ipc", "show"])
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to fetch IPC targets: {e}", file=sys.stderr)

def handle_ipc(target: str, method: str, args: list, quiet: bool):
    cmd = ["quickshell", "ipc", "call", target, method] + args
    try:
        stdout = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, check=True, stdout=stdout)
    except subprocess.CalledProcessError as e:
        print(f"[-] IPC Call failed: {e}", file=sys.stderr)
