"""
Unit tests for YAML parsing and serialization.
"""

import pytest
import yaml

from tree_package import (
    yaml_to_tree,
    tree_to_yaml,
    TreeConfig,
    TreeType,
)
from tree_package.exceptions import InvalidYAMLError
from tree_package.binary_tree import BinaryTreeOperations
from tree_package.general_tree import GeneralTreeOperations


# Sample YAML for binary tree
BINARY_YAML = """
value: 1
left:
  value: 2
  left:
    value: 4
  right:
    value: 5
right:
  value: 3
"""

# Sample YAML for general tree
GENERAL_YAML = """
value: 1
children:
  - value: 2
    children:
      - value: 4
      - value: 5
  - value: 3
    children: []
"""


class TestYAMLToBinaryTree:
    """Tests for YAML -> Binary Tree."""

    def test_parse_binary_tree(self):
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(BINARY_YAML, config=config)
        assert root is not None
        assert root.value == 1
        assert root.left.value == 2
        assert root.right.value == 3
        assert root.left.left.value == 4
        assert root.left.right.value == 5

    def test_parse_empty(self):
        root = yaml_to_tree("null", config=TreeConfig(tree_type=TreeType.BINARY))
        assert root is None

    def test_parse_scalar_leaf(self):
        root = yaml_to_tree("42", config=TreeConfig(tree_type=TreeType.BINARY))
        assert root.value == 42
        assert root.left is None
        assert root.right is None

    def test_malformed_yaml_raises(self):
        with pytest.raises(InvalidYAMLError):
            yaml_to_tree("[1, 2,", config=TreeConfig(tree_type=TreeType.BINARY))

    def test_missing_value_raises(self):
        with pytest.raises(InvalidYAMLError):
            yaml_to_tree(
                "left: null\nright: null",
                config=TreeConfig(tree_type=TreeType.BINARY),
            )

    def test_graceful_missing_children_binary(self):
        """Missing left or right keys are handled as no child (graceful)."""
        # Only left child present; right omitted entirely
        yaml_only_left = """
value: 1
left:
  value: 2
"""
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(yaml_only_left, config=config)
        assert root is not None
        assert root.value == 1
        assert root.left is not None
        assert root.left.value == 2
        assert root.right is None
        # Round-trip: tree -> YAML -> tree
        out = tree_to_yaml(root, config=config)
        root2 = yaml_to_tree(out, config=config)
        assert root2.value == 1
        assert root2.left.value == 2
        assert root2.right is None


class TestYAMLToGeneralTree:
    """Tests for YAML -> General Tree."""

    def test_parse_general_tree(self):
        config = TreeConfig(tree_type=TreeType.GENERAL)
        root = yaml_to_tree(GENERAL_YAML, config=config)
        assert root is not None
        assert root.value == 1
        assert len(root.children) == 2
        assert root.children[0].value == 2
        assert root.children[1].value == 3
        assert root.children[0].children[0].value == 4
        assert root.children[0].children[1].value == 5

    def test_graceful_missing_children_general(self):
        """Missing or empty children key is handled as leaf (graceful)."""
        yaml_leaf = "value: block_0\n"
        config = TreeConfig(tree_type=TreeType.GENERAL)
        root = yaml_to_tree(yaml_leaf, config=config)
        assert root is not None
        assert root.value == "block_0"
        assert root.children == []


class TestTreeToYAML:
    """Tests for Tree -> YAML serialization."""

    def test_serialize_binary_tree(self):
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(BINARY_YAML, config=config)
        out = tree_to_yaml(root, config=config)
        parsed = yaml.safe_load(out)
        assert parsed["value"] == 1
        assert parsed["left"]["value"] == 2
        assert parsed["right"]["value"] == 3

    def test_serialize_empty(self):
        out = tree_to_yaml(None)
        assert "null" in out or out.strip() == "null"

    def test_roundtrip_binary(self):
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(BINARY_YAML, config=config)
        out = tree_to_yaml(root, config=config)
        root2 = yaml_to_tree(out, config=config)
        assert root.value == root2.value
        assert root.left.value == root2.left.value
        assert root.right.value == root2.right.value

    def test_optional_cfd_fields_ignored_when_absent(self):
        """YAML without CFD fields parses as before (backward compatibility)."""
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(BINARY_YAML, config=config)
        assert root.value == 1
        assert getattr(root, "block_index", None) is None

    def test_optional_cfd_fields_parsed_when_present(self):
        """Optional CFD fields are accepted and preserved in round-trip."""
        yaml_with_cfd = """
value: 1
block_index: 0
block_dimensions: [10, 10, 10]
left:
  value: 2
  block_index: 1
right: null
"""
        config = TreeConfig(tree_type=TreeType.BINARY)
        root = yaml_to_tree(yaml_with_cfd, config=config)
        assert root.value == 1
        assert root.block_index == 0
        assert root.block_dimensions == (10, 10, 10)
        assert root.left.value == 2
        assert root.left.block_index == 1
        out = tree_to_yaml(root, config=config)
        root2 = yaml_to_tree(out, config=config)
        assert root2.block_index == 0
        assert root2.block_dimensions == (10, 10, 10)
