"""Deprecated alias of :mod:`gaig_toolkit.cli`. Use ``gaig`` or ``python -m gaig_toolkit.cli``."""

from gaig_toolkit.cli import build_parser, main, program_name

__all__ = ["build_parser", "main", "program_name"]


if __name__ == "__main__":
    main()
