"""
YAML integration: parse YAML → Tree, serialize Tree → YAML.

Human-readable recursive format with edge case handling.
Graceful handling of missing children: left/right (binary) and children (general)
may be omitted or null; missing keys are treated as no child.
Raises InvalidYAMLError on malformed YAML or missing required "value" key.
"""

import yaml
from typing import Optional, Any, Dict, Union

from tree_package.node import BinaryNode, GeneralNode
from tree_package.config import TreeConfig, TreeType
from tree_package.exceptions import InvalidYAMLError


def _parse_optional_cfd(data: dict) -> dict:
    """
    Extract optional CFD fields from node dict; ignore if absent.
    block_dimensions: list or tuple of ints (e.g. [nx, ny, nz]).
    block_index: int. adjacency: list of identifiers.
    """
    extra = {}
    if "block_dimensions" in data and data["block_dimensions"] is not None:
        dims = data["block_dimensions"]
        if isinstance(dims, (list, tuple)) and all(isinstance(x, int) for x in dims):
            extra["block_dimensions"] = tuple(dims)
    if "block_index" in data and data["block_index"] is not None:
        idx = data["block_index"]
        if isinstance(idx, int):
            extra["block_index"] = idx
    if "adjacency" in data and data["adjacency"] is not None:
        adj = data["adjacency"]
        if isinstance(adj, (list, tuple)):
            extra["adjacency"] = list(adj)
    return extra


def _yaml_to_binary_node(data: Any) -> Optional[BinaryNode]:
    """
    Recursively build BinaryNode from dict.
    Format: { value: X, left: {...}, right: {...} }
    left/right optional; None or missing means no child.
    Optional CFD: block_dimensions, block_index, adjacency (ignored if absent).
    """
    if data is None:
        return None
    if isinstance(data, dict):
        value = data.get("value")
        if "value" not in data:
            raise InvalidYAMLError("Node dict must have 'value' key")
        left_data = data.get("left")
        right_data = data.get("right")
        left = _yaml_to_binary_node(left_data) if left_data is not None else None
        right = _yaml_to_binary_node(right_data) if right_data is not None else None
        cfd = _parse_optional_cfd(data)
        return BinaryNode(value=value, left=left, right=right, **cfd)
    # Scalar: treat as leaf
    return BinaryNode(value=data)


def _yaml_to_general_node(data: Any) -> Optional[GeneralNode]:
    """
    Recursively build GeneralNode from dict.
    Format: { value: X, children: [...] }
    children optional; empty or missing means leaf.
    Optional CFD: block_dimensions, block_index, adjacency (ignored if absent).
    """
    if data is None:
        return None
    if isinstance(data, dict):
        value = data.get("value")
        if "value" not in data:
            raise InvalidYAMLError("Node dict must have 'value' key")
        children_data = data.get("children", [])
        if not isinstance(children_data, (list, tuple)):
            raise InvalidYAMLError(
                f"'children' must be list, got {type(children_data).__name__}"
            )
        children = []
        for c in children_data:
            n = _yaml_to_general_node(c)
            if n is not None:
                children.append(n)
        cfd = _parse_optional_cfd(data)
        return GeneralNode(value=value, children=children, **cfd)
    return GeneralNode(value=data)


def _binary_node_to_yaml(node: BinaryNode) -> Dict[str, Any]:
    """Serialize BinaryNode to dict for YAML; include optional CFD fields if set."""
    result: Dict[str, Any] = {"value": node.value}
    if node.left is not None:
        result["left"] = _binary_node_to_yaml(node.left)
    if node.right is not None:
        result["right"] = _binary_node_to_yaml(node.right)
    if getattr(node, "block_dimensions", None) is not None:
        result["block_dimensions"] = list(node.block_dimensions)
    if getattr(node, "block_index", None) is not None:
        result["block_index"] = node.block_index
    if getattr(node, "adjacency", None) is not None:
        result["adjacency"] = node.adjacency
    return result


def _general_node_to_yaml(node: GeneralNode) -> Dict[str, Any]:
    """Serialize GeneralNode to dict for YAML; include optional CFD fields if set."""
    result: Dict[str, Any] = {"value": node.value}
    if node.children:
        result["children"] = [_general_node_to_yaml(c) for c in node.children]
    if getattr(node, "block_dimensions", None) is not None:
        result["block_dimensions"] = list(node.block_dimensions)
    if getattr(node, "block_index", None) is not None:
        result["block_index"] = node.block_index
    if getattr(node, "adjacency", None) is not None:
        result["adjacency"] = node.adjacency
    return result


def yaml_to_tree(
    yaml_str: str, config: Optional[TreeConfig] = None
) -> Optional[Union[BinaryNode, GeneralNode]]:
    """
    Parse YAML string into tree.

    Args:
        yaml_str: YAML content as string.
        config: Tree config (default: binary).

    Returns:
        Root node (BinaryNode or GeneralNode) or None if empty.

    Raises:
        InvalidYAMLError: On malformed YAML or structure.
    """
    if config is None:
        config = TreeConfig()
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise InvalidYAMLError(f"YAML parse error: {e}") from e

    if data is None:
        return None

    if config.tree_type == TreeType.BINARY:
        return _yaml_to_binary_node(data)
    return _yaml_to_general_node(data)


def tree_to_yaml(
    root: Optional[Union[BinaryNode, GeneralNode]],
    config: Optional[TreeConfig] = None,
) -> str:
    """
    Serialize tree to YAML string.

    Args:
        root: Root node (None = empty).
        config: Tree config (default: binary).

    Returns:
        YAML string (human-readable, recursive).
    """
    if config is None:
        config = TreeConfig()
    if root is None:
        return "null"

    if hasattr(root, "left") and hasattr(root, "right"):
        data = _binary_node_to_yaml(root)
    elif hasattr(root, "children"):
        data = _general_node_to_yaml(root)
    else:
        raise InvalidYAMLError(f"Unknown node type: {type(root)}")

    return yaml.dump(data, default_flow_style=False, allow_unicode=True)
