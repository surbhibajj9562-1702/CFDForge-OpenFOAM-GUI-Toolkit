"""
General Tree implementation (n children per node).

Operations as helper/service functions - same pattern as binary tree.
"""

from typing import Optional, Any, List, Tuple

from tree_package.node import GeneralNode
from tree_package.exceptions import InvalidPathError, NodeNotFoundError


def create_general_tree(root_value: Any) -> Optional[GeneralNode]:
    """
    Create a new general tree with a single root node.

    Args:
        root_value: Value for the root node.

    Returns:
        Root GeneralNode, or None if root_value is None (empty tree).
    """
    if root_value is None:
        return None
    return GeneralNode(value=root_value)


def _validate_general_path(path: str) -> List[int]:
    """
    Validate path for general tree.
    Format: "0,1,2" or "0.1.2" for indices into children lists.
    Returns list of indices.
    """
    if not isinstance(path, str):
        raise InvalidPathError(f"Path must be str, got {type(path).__name__}")
    path = path.strip()
    if not path:
        return []
    parts = path.replace(".", ",").split(",")
    indices = []
    for p in parts:
        p = p.strip()
        if not p.isdigit():
            raise InvalidPathError(
                f"Path must contain non-negative integer indices separated by ',' or '.', got: '{path}'"
            )
        indices.append(int(p))
    return indices


def _follow_general_path(root: GeneralNode, path: str) -> GeneralNode:
    """Follow path (indices) from root to target node."""
    indices = _validate_general_path(path)
    node = root
    for i, idx in enumerate(indices):
        if idx < 0 or idx >= len(node.children):
            raise NodeNotFoundError(
                f"Child index {idx} out of range at depth {i} (node has {len(node.children)} children)"
            )
        node = node.children[idx]
    return node


class GeneralTreeOperations:
    """
    Service class for general tree operations.
    """

    @staticmethod
    def add_node_by_path(
        root: Optional[GeneralNode], path: str, value: Any
    ) -> GeneralNode:
        """
        Add a node as child at the given path.
        New node is appended as last child of the node at path.
        """
        if root is None:
            if path:
                raise NodeNotFoundError("Cannot add with path on empty tree")
            return GeneralNode(value=value)

        if not path:
            root.children.append(GeneralNode(value=value))
            return root

        parent = _follow_general_path(root, path)
        parent.children.append(GeneralNode(value=value))
        return root

    @staticmethod
    def add_node_at_index(
        root: Optional[GeneralNode], path: str, index: int, value: Any
    ) -> GeneralNode:
        """Add node at specific child index."""
        if root is None:
            if path:
                raise NodeNotFoundError("Cannot add with path on empty tree")
            return GeneralNode(value=value)

        if not path:
            if index < 0 or index > len(root.children):
                raise InvalidPathError(
                    f"Index {index} out of range for root (has {len(root.children)} children)"
                )
            root.children.insert(index, GeneralNode(value=value))
            return root

        parent = _follow_general_path(root, path)
        if index < 0 or index > len(parent.children):
            raise InvalidPathError(
                f"Index {index} out of range (node has {len(parent.children)} children)"
            )
        parent.children.insert(index, GeneralNode(value=value))
        return root

    @staticmethod
    def delete_node(
        root: Optional[GeneralNode], path: str
    ) -> Tuple[Optional[GeneralNode], Optional[GeneralNode]]:
        """
        Delete node at path.
        Path format: "0" for first child of root, "0,1" for second child of first child, etc.
        """
        if root is None:
            raise NodeNotFoundError("Cannot delete from empty tree")

        indices = _validate_general_path(path)
        if not indices:
            return (None, root)

        if len(indices) == 1:
            idx = indices[0]
            if idx < 0 or idx >= len(root.children):
                raise NodeNotFoundError(
                    f"Child index {idx} not found at root (has {len(root.children)} children)"
                )
            deleted = root.children.pop(idx)
            return (root, deleted)

        parent_path_indices = indices[:-1]
        last_idx = indices[-1]
        parent = _follow_general_path(root, ",".join(map(str, parent_path_indices)))
        if last_idx < 0 or last_idx >= len(parent.children):
            raise NodeNotFoundError(
                f"Child index {last_idx} not found (node has {len(parent.children)} children)"
            )
        deleted = parent.children.pop(last_idx)
        return (root, deleted)

    @staticmethod
    def delete_tree(root: Optional[GeneralNode]) -> None:
        """Recursively delete entire tree."""
        if root is None:
            return
        for child in root.children:
            GeneralTreeOperations.delete_tree(child)
        root.children.clear()

    @staticmethod
    def edit_node_value(
        root: Optional[GeneralNode], path: str, value: Any
    ) -> GeneralNode:
        """Edit the value of node at path."""
        if root is None:
            raise NodeNotFoundError("Cannot edit empty tree")
        node = _follow_general_path(root, path)
        node.value = value
        return root

    @staticmethod
    def get_node(root: Optional[GeneralNode], path: str) -> Optional[GeneralNode]:
        """Get node at path, or None if not found."""
        if root is None:
            return None
        try:
            return _follow_general_path(root, path)
        except (InvalidPathError, NodeNotFoundError):
            return None

    @staticmethod
    def print_tree(
        root: Optional[GeneralNode],
        indent: str = "",
        prefix: str = "",
        is_last: bool = True,
    ) -> str:
        """Pretty-format general tree for display."""
        if root is None:
            return ""

        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(indent + prefix + connector + str(root.value))

        new_indent = indent + ("    " if is_last else "│   ")
        for i, child in enumerate(root.children):
            child_last = i == len(root.children) - 1
            child_prefix = f"[{i}]: "
            lines.append(
                GeneralTreeOperations.print_tree(
                    child, new_indent, child_prefix, child_last
                )
            )

        return "\n".join(lines)

    @staticmethod
    def print_subtree(root: Optional[GeneralNode], from_path: str = "") -> str:
        """Print subtree rooted at given path."""
        if root is None:
            return "(empty tree)"
        node = root if not from_path else _follow_general_path(root, from_path)
        return GeneralTreeOperations.print_tree(node)
