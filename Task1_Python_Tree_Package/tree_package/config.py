"""
Configuration for tree type switching.

Allows switching between Binary Tree and General Tree via config.
Aligned with OpenFOAM-style hierarchical configuration (e.g. block structure,
solver parameters) where YAML mirrors dictionary-like nesting.
"""

from enum import Enum
from dataclasses import dataclass


class TreeType(str, Enum):
    """Supported tree types (binary = two children; general = any number)."""

    BINARY = "binary"
    GENERAL = "general"


@dataclass
class TreeConfig:
    """
    Configuration for tree creation and behavior.

    Attributes:
        tree_type: Binary or General tree. General tree supports
            arbitrary branching (e.g. multi-block CFD domain with N neighbours).
    """

    tree_type: TreeType = TreeType.BINARY
