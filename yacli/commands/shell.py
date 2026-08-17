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
    cmd = ["quickshell", "ipc", "call", target, method]
    try:
        stdout = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, check=True, stdout=stdout)
    except subprocess.CalledProcessError as e:
        print(f"[-] IPC Call failed: {e}", file=sys.stderr)

def handle_shell_config(args=None):
    """Opens the quickshell directory in Neovim / $EDITOR."""
    # Fall back to 'nvim' if $EDITOR environment variable isn't set
    editor = os.environ.get("EDITOR", "nvim")
    
    if not DEFAULT_CONFIG_DIR.exists():
        print(f"[-] Config directory not found: {DEFAULT_CONFIG_DIR}")
        return

    # Launches 'nvim ~/.config/quickshell'
    subprocess.run([editor, str(DEFAULT_CONFIG_DIR)])

def handle_refresh(config_dir: Path, config_file: str, verbose: bool, quiet: bool):
    """Refreshes Quickshell by triggering an IPC reload or running a clean restart."""
    if not quiet:
        print("[*] Refreshing yamd3s shell...")
    
    try:
        res = subprocess.run(
            ["quickshell", "ipc", "call", "shell", "refresh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if res.returncode == 0:
            if not quiet:
                print("[+] Shell reloaded successfully via IPC!")
            return
    except Exception:
        pass

    if not quiet:
        print("[*] IPC reload not available. Performing restart...")
    handle_kill(quiet=True)
    handle_run(config_dir, config_file, verbose, quiet)

def handle_install(target_dir: str, verbose: bool, quiet: bool):
    """Clones or updates yamd3s into the target directory and sets up the version file."""
    config_dir = Path(target_dir).expanduser().resolve()
    version_file = config_dir / ".yacli-version"
    anchor_file = config_dir / "Y3s" / "Globals.qml"
    repo_url = "https://github.com/sol-less/yamd3s.git"
    latest_version = "1.0.5"

    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] Error: 'git' is not installed or not in PATH.", file=sys.stderr)
        return

    stdout_mode = None if verbose else subprocess.DEVNULL

    if version_file.exists():
        installed_version = version_file.read_text().strip()
        if not quiet:
            print(f"[+] yamd3s is already installed at {config_dir} (Version: {installed_version})")
        
        if installed_version != latest_version:
            if not quiet:
                print(f"[*] Updating yamd3s to version {latest_version}...")
            try:
                subprocess.run(["git", "pull", "origin", "main"], cwd=config_dir, check=True, stdout=stdout_mode)
                version_file.write_text(latest_version)
                if not quiet:
                    print("[+] Update complete!")
            except subprocess.CalledProcessError as e:
                print(f"[-] Update failed: {e}", file=sys.stderr)

    elif anchor_file.exists():
        if not quiet:
            print("[-] Warning: .yacli-version is missing, but yamd3s files were found. Repairing...")
        version_file.write_text(latest_version)
        if not quiet:
            print("[+] Repair complete!")

    else:
        if not quiet:
            print(f"[*] Installing yamd3s into {config_dir}...")
        
        config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run(["git", "init"], cwd=config_dir, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=config_dir, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "fetch", "origin"], cwd=config_dir, check=True, stdout=stdout_mode)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=config_dir, check=True, stdout=stdout_mode)
            
            version_file.write_text(latest_version)
            if not quiet:
                print("[+] Install complete! Run 'yacli shell build' to compile your modules.")
        except subprocess.CalledProcessError as e:
            print(f"[-] Install failed: {e}", file=sys.stderr)
