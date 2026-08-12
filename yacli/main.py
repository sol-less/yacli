import argparse
import sys
from pathlib import Path
from yacli.commands.shell import (
    DEFAULT_CONFIG_DIR,
    handle_build,
    handle_run,
    handle_kill,
    handle_list,
    handle_ipc_list,
    handle_ipc
)
from yacli.commands.picker import handle_picker

def main():
    parser = argparse.ArgumentParser(prog="yacli", description="CLI controller for yamd3s")
    
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output", default=False)
    output_group.add_argument("-q", "--quiet", action="store_true", help="Suppress output messages", default=False)

    subparsers = parser.add_subparsers(dest="command")

    # Shell command group
    shell_parser = subparsers.add_parser("shell", help="Manage the yamd3s shell environment")
    shell_parser.add_argument("-c", "--config", type=str, help="Path to custom Quickshell config file")
    shell_parser.add_argument("-l", "--list", action="store_true", help="List generated modules and exit")

    shell_subparsers = shell_parser.add_subparsers(dest="shell_action")
    shell_subparsers.add_parser("build", help="Run CMake build for modules")
    shell_subparsers.add_parser("run", help="Run the yamd3s shell")
    shell_subparsers.add_parser("kill", help="Kill quickshell instances")

    ipc_parser = shell_subparsers.add_parser("ipc", help="Send IPC call to quickshell")
    ipc_parser.add_argument("-l", "--list", action="store_true", help="List active IPC targets and methods")
    ipc_parser.add_argument("method", nargs="?", help="Method/action to trigger inside IpcHandler")
    ipc_parser.add_argument("--target", default="yamd3s", help="IPC target name (default: yamd3s)")
    ipc_parser.add_argument("args", nargs="*", help="Optional arguments for the IPC method")

    # Picker command group
    picker_parser = subparsers.add_parser("picker", help="Pick a color using hyprpicker")
    picker_parser.add_argument("-f", "--format", choices=["hex", "rgb", "hsl", "hsv", "cmyk"], default="hex", help="Color format output")
    picker_parser.add_argument("-n", "--notify", action="store_true", help="Send desktop notification upon picking")

    args = parser.parse_args()

    if args.command == "shell":
        if args.list:
            handle_list(DEFAULT_CONFIG_DIR)
            return

        if args.shell_action == "build":
            handle_build(DEFAULT_CONFIG_DIR, args.verbose, args.quiet)
        elif args.shell_action == "run":
            handle_run(DEFAULT_CONFIG_DIR, args.config, args.verbose, args.quiet)
        elif args.shell_action == "kill":
            handle_kill(args.quiet)
        elif args.shell_action == "ipc":
            if args.list:
                handle_ipc_list()
            elif args.method:
                handle_ipc(args.target, args.method, args.args, args.quiet)
            else:
                ipc_parser.print_help()
        else:
            shell_parser.print_help()

    elif args.command == "picker":
        handle_picker(args.format, args.notify, args.quiet)
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
