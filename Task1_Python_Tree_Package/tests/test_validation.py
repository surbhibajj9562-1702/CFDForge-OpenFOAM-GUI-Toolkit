"""
Unit tests for tree validation.
"""

import pytest

from tree_package import create_binary_tree, BinaryTreeOperations
from tree_package.validation import validate_no_cycles, validate_tree
from tree_package.exceptions import ValidationError


class TestValidation:
    """Tests for tree validation."""

    def test_validate_empty(self):
        assert validate_no_cycles(None) is True
        assert validate_tree(None) is True

    def test_validate_simple_tree(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        assert validate_tree(root) is True
