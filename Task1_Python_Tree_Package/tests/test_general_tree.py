"""
Unit tests for general tree operations.
"""

import pytest

from tree_package import create_general_tree, GeneralTreeOperations
from tree_package.exceptions import InvalidPathError, NodeNotFoundError


class TestCreateGeneralTree:
    """Tests for create_general_tree."""

    def test_create_empty(self):
        assert create_general_tree(None) is None

    def test_create_single_node(self):
        root = create_general_tree("root")
        assert root is not None
        assert root.value == "root"
        assert root.children == []


class TestAddNodeGeneral:
    """Tests for add_node_by_path on general tree."""

    def test_add_first_child(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        assert len(root.children) == 1
        assert root.children[0].value == 2

    def test_add_multiple_children(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root = GeneralTreeOperations.add_node_by_path(root, "", 3)
        root = GeneralTreeOperations.add_node_by_path(root, "", 4)
        assert len(root.children) == 3
        assert [c.value for c in root.children] == [2, 3, 4]

    def test_add_deep_path(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root = GeneralTreeOperations.add_node_by_path(root, "0", 3)
        root = GeneralTreeOperations.add_node_by_path(root, "0,0", 4)
        # 4 is child of 3 (which is first child of 2)
        assert root.children[0].children[0].children[0].value == 4

    def test_path_dot_separator(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root = GeneralTreeOperations.add_node_by_path(root, "0", 3)  # 3 is child of 2
        assert root.children[0].children[0].value == 3
        root = GeneralTreeOperations.add_node_by_path(root, "0.0", 4)  # 4 is child of 3
        assert root.children[0].children[0].children[0].value == 4


class TestDeleteNodeGeneral:
    """Tests for delete_node on general tree."""

    def test_delete_child(self):
        root = create_general_tree(1)
        root = GeneralTreeOperations.add_node_by_path(root, "", 2)
        root, deleted = GeneralTreeOperations.delete_node(root, "0")
        assert len(root.children) == 0
        assert deleted.value == 2
