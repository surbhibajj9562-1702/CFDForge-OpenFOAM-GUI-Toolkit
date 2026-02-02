"""
Tree validation checks: cycles, structure integrity.
"""

from typing import Optional, Set, Union

from tree_package.node import BinaryNode, GeneralNode
from tree_package.exceptions import ValidationError


def _is_binary(node: any) -> bool:
    return hasattr(node, "left") and hasattr(node, "right")


def _is_general(node: any) -> bool:
    return hasattr(node, "children")


def _get_children(node: Union[BinaryNode, GeneralNode]):
    """Get children of node for traversal."""
    if _is_binary(node):
        result = []
        if node.left:
            result.append(node.left)
        if node.right:
            result.append(node.right)
        return result
    if _is_general(node):
        return list(node.children)
    return []


def validate_no_cycles(root: Optional[Union[BinaryNode, GeneralNode]]) -> bool:
    """
    Validate tree has no cycles (DAG check).
    Raises ValidationError if cycle detected.
    """
    if root is None:
        return True

    visited: Set[int] = set()

    def _check(node: Union[BinaryNode, GeneralNode], path_ids: Set[int]) -> None:
        node_id = id(node)
        if node_id in path_ids:
            raise ValidationError("Cycle detected in tree structure")
        if node_id in visited:
            return
        visited.add(node_id)
        path_ids.add(node_id)
        try:
            for child in _get_children(node):
                _check(child, path_ids)
        finally:
            path_ids.discard(node_id)

    _check(root, set())
    return True


def validate_tree(root: Optional[Union[BinaryNode, GeneralNode]]) -> bool:
    """
    Run all validation checks on tree.
    Raises ValidationError on failure.
    """
    validate_no_cycles(root)
    return True
