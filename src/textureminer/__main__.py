"""Entry point for the textureminer CLI."""

import sys

from .cli import cli

if __name__ == '__main__':
    sys.exit(cli())
