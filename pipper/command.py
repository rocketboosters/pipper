import sys

import pipper
from pipper import authorizer
from pipper import bundler
from pipper import downloader
from pipper import info
from pipper import installer
from pipper import parser
from pipper import publisher
from pipper import repository
from pipper.environment import Environment

ACTIONS = {
    "authorize": authorizer.run,
    "download": downloader.run,
    "install": installer.run,
    "bundle": bundler.run,
    "publish": publisher.run,
    "info": info.run,
    "repository": repository.run,
}


def show_version(env: Environment):
    """Shows the pipper version information and then exits"""
    if env.quiet:
        print(pipper.__version__)
    else:
        print(f"Version: {pipper.__version__}")


def run(cli_args: list | None = None):
    """Executes the command based on command line arguments."""
    args = parser.parse(cli_args)
    env = Environment(args)

    if args.get("version"):
        show_version(env)
        sys.exit(0)

    action = ACTIONS.get(env.action)
    if action is None:
        message = f'Unrecognized command action "{env.action}"'
        print(f"[ERROR]: {message}")
        args["parser"].print_help()
        raise ValueError(message)

    if not env.quiet:
        print(f"\n\n=== {env.action.upper()} ===\n")

    try:
        action(env)
    except Exception as err:
        print(f"[ERROR]: Unable to complete action. {err}\n")
        raise

    if not env.quiet:
        print("\n")
