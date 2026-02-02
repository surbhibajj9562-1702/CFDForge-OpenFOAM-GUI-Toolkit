"""
Custom exceptions for the tree package.

Provides clean, meaningful error messages for evaluator-friendly debugging.
"""


class TreeError(Exception):
    """Base exception for all tree-related errors."""

    pass


class InvalidPathError(TreeError):
    """Raised when a path string is invalid (e.g., non-L/R characters)."""

    pass


class NodeNotFoundError(TreeError):
    """Raised when a node cannot be found at the given path."""

    pass


class InvalidYAMLError(TreeError):
    """Raised when YAML parsing fails or structure is malformed."""

    pass


class ValidationError(TreeError):
    """Raised when tree validation fails (e.g., cycle detection)."""

    pass
