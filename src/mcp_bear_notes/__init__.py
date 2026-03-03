"""MCP Bear Notes Server - Model Context Protocol integration for Bear Notes."""

from .server import main, run
from .bear_client import BearNotesClient

__version__ = "0.1.0"
__all__ = ["main", "run", "BearNotesClient"]

# Made with Bob
