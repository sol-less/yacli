# [ Yacli ]
> a CLI tool for **Yamd3s**

---

# Installation

Ensure you have these dependencies that is required for the installation:

* **Python 3.10+**
* **Quickshell**
* **Hyprpicker** -> requires **Hyprland**
* **wl-copy**

> [!NOTE]
> Install it via your system's package manager.

## Option 1: Manual
> or, the recommended way.

```bash
git clone [https://github.com/sol-less/yacli](https://github.com/sol-less/yacli)
cd yacli/
pip install . --break-system-packages
```

Run the build script:
```bash
python scripts/build.py
```

And make it universal on your device:
```bash
mkdir -p ~/.local/bin && mv dist/yacli ~/.local/bin/yacli
```

> [!IMPORTANT]
> Make sure `~/.local/bin` is in your `$PATH` before running `yacli`.

## Option 2: AUR Install
> [!NOTE]
> AUR Install is **still** not available, sorry!

# Usage
- Use ```yacli``` to show universal help
- Use ```yacli shell``` to show Quickshell-focused help
---
