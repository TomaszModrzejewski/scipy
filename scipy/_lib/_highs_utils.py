"""Helper functions to get location of source files."""

import pathlib


def _highs_dir() -> pathlib.Path:
    """Directory where root highs/ directory lives."""
    return pathlib.Path(__file__).parent / 'highs'
