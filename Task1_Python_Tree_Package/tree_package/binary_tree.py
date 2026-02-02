"""
Binary Tree implementation with operations as helper/service functions.

Node class is kept lean; operations live in BinaryTreeOperations.
"""

from typing import Optional, Any, Tuple

from tree_package.node import BinaryNode
from tree_package.exceptions import InvalidPathError, NodeNotFoundError


def create_binary_tree(root_value: Any) -> Optional[BinaryNode]:
    """
    Create a new binary tree with a single root node.

    Args:
        root_value: Value for the root node.

    Returns:
        Root BinaryNode, or None if root_value is None (empty tree).
    """
    if root_value is None:
        return None
    return BinaryNode(value=root_value)


def _validate_path(path: str) -> None:
    """Validate path contains only L and R characters."""
    if not isinstance(path, str):
        raise InvalidPathError(f"Path must be str, got {type(path).__name__}")
    path = path.strip().upper()
    if path and not all(c in "LR" for c in path):
        raise InvalidPathError(
            f"Path must contain only 'L' or 'R' (case-insensitive), got: '{path}'"
        )


def _follow_path(root: BinaryNode, path: str) -> BinaryNode:
    """
    Follow path from root to target node.
    Path: "" = root, "L" = left child, "R" = right, "LL" = left of left, etc.
    """
    _validate_path(path)
    node = root
    path = path.strip().upper()
    for step in path:
        if step == "L":
            if node.left is None:
                raise NodeNotFoundError(
                    f"No left child at path '{path[:path.index(step)+1]}'"
                )
            node = node.left
        else:  # R
            if node.right is None:
                raise NodeNotFoundError(
                    f"No right child at path '{path[:path.index(step)+1]}'"
                )
            node = node.right
    return node


class BinaryTreeOperations:
    """
    Service class for binary tree operations.

    All operations are static/class methods - no bloat on Node.
    """

    @staticmethod
    def add_node_by_path(
        root: Optional[BinaryNode], path: str, value: Any, side: str = "L"
    ) -> BinaryNode:
        """
        Add a node at the given path. Creates intermediate nodes if needed.

        Args:
            root: Root of tree (creates new tree if None).
            path: Path to parent ("" for root).
            value: Value for new node.
            side: 'L' or 'R' - which child to add.

        Returns:
            Root of tree (possibly new root if original was None).
        """
        side = side.upper()
        if side not in ("L", "R"):
            raise InvalidPathError(f"Side must be 'L' or 'R', got '{side}'")

        if root is None:
            if path:
                raise NodeNotFoundError("Cannot add with path on empty tree")
            return BinaryNode(value=value)

        if not path:
            # Adding as child of root
            new_node = BinaryNode(value=value)
            if side == "L":
                if root.left is not None:
                    raise InvalidPathError(
                        "Left child already exists at root - use edit or delete first"
                    )
                root.left = new_node
            else:
                if root.right is not None:
                    raise InvalidPathError(
                        "Right child already exists at root - use edit or delete first"
                    )
                root.right = new_node
            return root

        parent = _follow_path(root, path)
        new_node = BinaryNode(value=value)
        if side == "L":
            if parent.left is not None:
                raise InvalidPathError(
                    f"Left child already exists at path '{path}L'"
                )
            parent.left = new_node
        else:
            if parent.right is not None:
                raise InvalidPathError(
                    f"Right child already exists at path '{path}R'"
                )
            parent.right = new_node
        return root

    @staticmethod
    def delete_node(
        root: Optional[BinaryNode], path: str
    ) -> Tuple[Optional[BinaryNode], Optional[BinaryNode]]:
        """
        Delete node at path. Returns (new_root, deleted_node).

        If deleting root, returns (None, old_root) when tree becomes empty,
        or (child, old_root) when root has single child.
        """
        if root is None:
            raise NodeNotFoundError("Cannot delete from empty tree")

        if not path:
            # Deleting root
            return (None, root)

        parent_path = path[:-1]
        step = path[-1].upper()
        try:
            parent = _follow_path(root, parent_path)
        except NodeNotFoundError:
            raise NodeNotFoundError(f"Parent not found for path '{path}'")

        if step == "L":
            if parent.left is None:
                raise NodeNotFoundError(f"No node at path '{path}'")
            deleted = parent.left
            parent.left = None
        else:
            if parent.right is None:
                raise NodeNotFoundError(f"No node at path '{path}'")
            deleted = parent.right
            parent.right = None

        return (root, deleted)

    @staticmethod
    def delete_tree(root: Optional[BinaryNode]) -> None:
        """
        Recursively delete entire tree (in-place clear of references).
        Caller should set their root reference to None after.
        """
        if root is None:
            return
        BinaryTreeOperations.delete_tree(root.left)
        BinaryTreeOperations.delete_tree(root.right)
        root.left = None
        root.right = None

    @staticmethod
    def edit_node_value(root: Optional[BinaryNode], path: str, value: Any) -> BinaryNode:
        """Edit the value of node at path."""
        if root is None:
            raise NodeNotFoundError("Cannot edit empty tree")
        node = _follow_path(root, path)
        node.value = value
        return root

    @staticmethod
    def get_node(root: Optional[BinaryNode], path: str) -> Optional[BinaryNode]:
        """Get node at path, or None if not found."""
        if root is None:
            return None
        try:
            return _follow_path(root, path)
        except (InvalidPathError, NodeNotFoundError):
            return None

    @staticmethod
    def print_tree(
        root: Optional[BinaryNode],
        indent: str = "",
        prefix: str = "",
        is_last: bool = True,
    ) -> str:
        """
        Pretty-format tree for display.
        Returns multiline string.
        """
        if root is None:
            return ""

        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(indent + prefix + connector + str(root.value))

        new_indent = indent + ("    " if is_last else "│   ")
        children: list[Tuple[Optional[BinaryNode], str]] = [
            (root.left, "L: "),
            (root.right, "R: "),
        ]
        for i, (child, label) in enumerate(children):
            if child is not None:
                child_prefix = label
                child_last = i == len(children) - 1 or (
                    i == 0 and children[1][0] is None
                )
                lines.append(
                    BinaryTreeOperations.print_tree(
                        child, new_indent, child_prefix, child_last
                    )
                )

        return "\n".join(lines)

    @staticmethod
    def print_subtree(root: Optional[BinaryNode], from_path: str = "") -> str:
        """
        Print subtree rooted at given path.
        If from_path is "", prints full tree.
        """
        if root is None:
            return "(empty tree)"
        node = root if not from_path else _follow_path(root, from_path)
        return BinaryTreeOperations.print_tree(node)
