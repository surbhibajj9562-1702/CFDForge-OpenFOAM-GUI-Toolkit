"""
CFD-FOSSEE Tree Package - Binary and General Tree with YAML Support.

A pip-installable package for working with tree structures (binary and general),
with YAML serialization, traversal utilities, and CLI support.
"""

from tree_package.config import TreeConfig, TreeType
from tree_package.exceptions import (
    TreeError,
    InvalidPathError,
    NodeNotFoundError,
    InvalidYAMLError,
    ValidationError,
)
from tree_package.node import BinaryNode, GeneralNode
from tree_package.binary_tree import create_binary_tree, BinaryTreeOperations
from tree_package.general_tree import create_general_tree, GeneralTreeOperations
from tree_package.yaml_handler import tree_to_yaml, yaml_to_tree
from tree_package.traversal import TraversalMixin

__version__ = "1.0.0"
__all__ = [
    "TreeConfig",
    "TreeType",
    "TreeError",
    "InvalidPathError",
    "NodeNotFoundError",
    "InvalidYAMLError",
    "ValidationError",
    "BinaryNode",
    "GeneralNode",
    "create_binary_tree",
    "create_general_tree",
    "BinaryTreeOperations",
    "GeneralTreeOperations",
    "tree_to_yaml",
    "yaml_to_tree",
    "TraversalMixin",
]
