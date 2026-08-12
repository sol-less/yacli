import subprocess
import sys

def handle_picker(fmt: str, notify: bool, quiet: bool):
    if not quiet:
        print(f"[*] Launching hyprpicker [{fmt}]...")

    cmd = ["hyprpicker", "-f", fmt]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        color = result.stdout.strip()

        if color:
            try:
                subprocess.run(["wl-copy", color], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            if not quiet:
                print(f"[+] Color picked: {color} (copied to clipboard)")
            
            if notify:
                subprocess.run(
                    ["notify-send", "Color Picked", f"Copied {color} to clipboard", "-i", "color-picker"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        if not quiet:
            print("\n[-] Color picker canceled.")
    except FileNotFoundError:
        print("[-] hyprpicker binary not found in PATH.", file=sys.stderr)
