"""CLI module for marketsched.

This module provides the command-line interface for marketsched,
built with Typer. Commands: bd, sq, ss, cache.
"""

from marketsched.cli.main import app, main

__all__ = ["app", "main"]
