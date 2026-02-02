"""
Unit tests for tree traversal utilities.
"""

import pytest

from tree_package import create_binary_tree, BinaryTreeOperations, TraversalMixin
from tree_package import create_general_tree, GeneralTreeOperations


class TestBinaryTraversal:
    """Tests for traversal on binary tree."""

    def test_preorder_binary(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        root = BinaryTreeOperations.add_node_by_path(root, "L", 4, "L")
        order = list(TraversalMixin.preorder(root))
        assert order == [1, 2, 4, 3]

    def test_inorder_binary(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        order = list(TraversalMixin.inorder(root))
        assert order == [2, 1, 3]

    def test_postorder_binary(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        order = list(TraversalMixin.postorder(root))
        assert order == [2, 3, 1]

    def test_level_order_binary(self):
        root = create_binary_tree(1)
        root = BinaryTreeOperations.add_node_by_path(root, "", 2, "L")
        root = BinaryTreeOperations.add_node_by_path(root, "", 3, "R")
        root = BinaryTreeOperations.add_node_by_path(root, "L", 4, "L")
        order = list(TraversalMixin.level_order(root))
        assert order == [1, 2, 3, 4]


class TestGeneralTraversal:
    """Tests for traversal on general tree."""

    def test_preorder_general(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root = GeneralTreeOperations.add_node_by_path(root, "", 3)
        root = GeneralTreeOperations.add_node_by_path(root, "0", 4)
        order = list(TraversalMixin.preorder(root))
        assert order == [1, 2, 4, 3]

    def test_level_order_general(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root = GeneralTreeOperations.add_node_by_path(root, "", 3)
        root = GeneralTreeOperations.add_node_by_path(root, "0", 4)
        order = list(TraversalMixin.level_order(root))
        assert order == [1, 2, 3, 4]
