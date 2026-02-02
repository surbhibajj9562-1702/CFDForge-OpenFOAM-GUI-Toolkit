"""
Unit tests for binary tree operations.
"""

import pytest

from tree_package import create_binary_tree, BinaryTreeOperations
from tree_package.exceptions import InvalidPathError, NodeNotFoundError
from tree_package.node import BinaryNode


class TestCreateTree:
    """Tests for create_binary_tree."""

    def test_create_empty(self):
        assert create_binary_tree(None) is None

    def test_create_single_node(self):
        root = create_binary_tree(42)
        assert root is not None
        assert root.value == 42
        assert root.left is None
        assert root.right is None


class TestAddNode:
    """Tests for add_node_by_path."""

    def test_add_left_at_root(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        assert root.left is not None
        assert root.left.value == 2

    def test_add_right_at_root(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        assert root.right is not None
        assert root.right.value == 3

    def test_add_deep_path(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        root = BinaryTreeOperations.add_node_by_path(root, "L", 4, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "L", 5, "R")
        assert root.left.left.value == 4
        assert root.left.right.value == 5

    def test_add_case_insensitive_path(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "l", 3, "l")  # path "l" = left of root
        assert root.left.left.value == 3

    def test_invalid_path_raises(self):
        root = create_binary_tree(1)
        with pytest.raises(InvalidPathError):
            BinaryTreeOperations.add_node_by_path(root, "LRX", 2, "L")

    def test_invalid_side_raises(self):
        root = create_binary_tree(1)
        with pytest.raises(InvalidPathError):
            BinaryTreeOperations.add_node_by_path(root, "", 2, "X")

    def test_duplicate_side_raises(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        with pytest.raises(InvalidPathError):
            BinaryTreeOperations.add_node_by_path(root, "", 3, "L")


class TestDeleteNode:
    """Tests for delete_node."""

    def test_delete_leaf(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root, deleted = BinaryTreeOperations.delete_node(root, "L")
        assert root.left is None
        assert deleted.value == 2

    def test_delete_from_empty_raises(self):
        with pytest.raises(NodeNotFoundError):
            BinaryTreeOperations.delete_node(None, "L")

    def test_delete_nonexistent_path_raises(self):
        root = create_binary_tree(1)
        with pytest.raises(NodeNotFoundError):
            BinaryTreeOperations.delete_node(root, "L")


class TestEditNode:
    """Tests for edit_node_value."""

    def test_edit_root(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.edit_node_value(root, "", 99)
        assert root.value == 99

    def test_edit_child(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.edit_node_value(root, "L", 20)
        assert root.left.value == 20


class TestPrintTree:
    """Tests for print_tree and print_subtree."""

    def test_print_empty(self):
        result = BinaryTreeOperations.print_tree(None)
        assert result == ""

    def test_print_single(self):
        root = create_binary_tree("A")
        result = BinaryTreeOperations.print_tree(root)
        assert "A" in result

    def test_print_subtree(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "L", 4, "L")
        result = BinaryTreeOperations.print_subtree(root, "L")
        assert "2" in result
        assert "4" in result
