import argparse
import sys
from pathlib import Path

from yacli.commands.picker import handle_picker
from yacli.commands.shell import (
    DEFAULT_CONFIG_DIR,
    handle_build,
    handle_ipc,
    handle_ipc_list,
    handle_kill,
    handle_list,
    handle_refresh,
    handle_run,
    handle_shell_config,
    handle_install
)


def main():
    # 1. Base parent parser for global flags (-v, -q)
    parent_parser = argparse.ArgumentParser(add_help=False)
    output_group = parent_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output", default=False
    )
    output_group.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output messages", default=False
    )

    # Main CLI parser inheriting global flags
    parser = argparse.ArgumentParser(
        prog="yacli",
        description="CLI controller for yamd3s",
        parents=[parent_parser],
    )

    subparsers = parser.add_subparsers(dest="command")

    # 2. Shell command group
    shell_parser = subparsers.add_parser(
        "shell", help="Manage the yamd3s shell environment", parents=[parent_parser]
    )
    shell_parser.add_argument(
        "-c", "--config", type=str, help="Path to custom Quickshell config file"
    )
    shell_parser.add_argument(
        "-l", "--list", action="store_true", help="List generated modules and exit"
    )

    shell_subparsers = shell_parser.add_subparsers(dest="shell_action")
    shell_subparsers.add_parser("build", help="Run CMake build for modules", parents=[parent_parser])
    shell_subparsers.add_parser("run", help="Run the yamd3s shell", parents=[parent_parser])
    shell_subparsers.add_parser("refresh", help="Refresh/reload the yamd3s shell", parents=[parent_parser])
    shell_subparsers.add_parser("kill", help="Kill quickshell instances", parents=[parent_parser])
    shell_subparsers.add_parser("config", help="Open quickshell configuration directory", parents=[parent_parser])

    # 3. Top-Level IPC command group (Allows `yacli ipc`)
    ipc_parser = subparsers.add_parser(
        "ipc", help="Send IPC call to quickshell", parents=[parent_parser]
    )
    ipc_parser.add_argument(
        "-l", "--list", action="store_true", help="List active IPC targets and methods"
    )
    ipc_parser.add_argument("method", nargs="?", help="Method/action to trigger inside IpcHandler")
    ipc_parser.add_argument("--target", default="yamd3s", help="IPC target name (default: yamd3s)")
    ipc_parser.add_argument("args", nargs="*", help="Optional arguments for the IPC method")

    # 4. Picker command group
    picker_parser = subparsers.add_parser(
        "picker", help="Pick a color using hyprpicker", parents=[parent_parser]
    )
    picker_parser.add_argument(
        "-f", "--format", choices=["hex", "rgb", "hsl", "hsv", "cmyk"], default="hex", help="Color format output"
    )
    picker_parser.add_argument(
        "-n", "--notify", action="store_true", help="Send desktop notification upon picking"
    )

    # 5. Install command group
    install_parser = subparsers.add_parser(
        "install", help="Install or download yamd3s files", parents=[parent_parser]
    )
    install_parser.add_argument("-d", "--dir", type=str, help="Target directory for the installation")

    args = parser.parse_args()

    # --- Execution Logic ---

    if args.command == "shell":
        if args.shell_action == "build":
            handle_build(DEFAULT_CONFIG_DIR, args.verbose, args.quiet)
        elif args.shell_action == "run":
            handle_run(DEFAULT_CONFIG_DIR, args.config, args.verbose, args.quiet)
        elif args.shell_action == "refresh":
            handle_refresh(DEFAULT_CONFIG_DIR, args.config, args.verbose, args.quiet)
        elif args.shell_action == "kill":
            handle_kill(args.quiet)
        elif args.shell_action == "config":
            handle_shell_config(DEFAULT_CONFIG_DIR)
        elif args.list:  # Handled only if no specific sub-action matched
            handle_list(DEFAULT_CONFIG_DIR)
        else:
            shell_parser.print_help()

    elif args.command == "ipc":
        if args.list:
            handle_ipc_list()
        elif args.method:
            handle_ipc(args.target, args.method, args.args, args.quiet)
        else:
            ipc_parser.print_help()

    elif args.command == "picker":
        handle_picker(args.format, args.notify, args.quiet)

    elif args.command == "install":
        target_dir = args.dir or input("Where do you want to download this? : ").strip()
        if target_dir:
            handle_install(target_dir, args.verbose, args.quiet)
        else:
            print("[-] Installation canceled: No directory provided.")

    else:
        parser.print_help()


def cli_entry():
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Operation canceled.")
        sys.exit(0)


if __name__ == "__main__":
    cli_entry()
