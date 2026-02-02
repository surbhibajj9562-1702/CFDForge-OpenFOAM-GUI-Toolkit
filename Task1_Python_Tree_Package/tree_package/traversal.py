"""
Tree traversal utilities: inorder, preorder, postorder, level-order.

Works with both BinaryNode and GeneralNode via duck typing.
"""

from typing import Iterator, Any, Callable, Union, Optional
from collections import deque

from tree_package.node import BinaryNode, GeneralNode


def _is_binary(node: Any) -> bool:
    """Check if node is BinaryNode (has left, right)."""
    return hasattr(node, "left") and hasattr(node, "right")


def _is_general(node: Any) -> bool:
    """Check if node is GeneralNode (has children list)."""
    return hasattr(node, "children")


class TraversalMixin:
    """
    Traversal utilities for trees.
    Use as mixin or call static methods directly.
    """

    @staticmethod
    def inorder(root: Optional[Union[BinaryNode, GeneralNode]]) -> Iterator[Any]:
        """
        Inorder traversal: left, root, right (binary) or children[0..k-1], root, children[k..] (general).
        For general tree: first half of children, root, rest of children (left-part, root, right-part).
        """
        if root is None:
            return
        if _is_binary(root):
            yield from TraversalMixin.inorder(root.left)
            yield root.value
            yield from TraversalMixin.inorder(root.right)
        elif _is_general(root):
            # For general: treat as left-half children, root, right-half children
            n = len(root.children)
            mid = n // 2
            for i in range(mid):
                yield from TraversalMixin.inorder(root.children[i])
            yield root.value
            for i in range(mid, n):
                yield from TraversalMixin.inorder(root.children[i])
        else:
            yield root.value

    @staticmethod
    def preorder(root: Optional[Union[BinaryNode, GeneralNode]]) -> Iterator[Any]:
        """
        Preorder traversal: root, then children.
        Binary: root, left, right.
        General: root, then each child in order.
        """
        if root is None:
            return
        yield root.value
        if _is_binary(root):
            yield from TraversalMixin.preorder(root.left)
            yield from TraversalMixin.preorder(root.right)
        elif _is_general(root):
            for child in root.children:
                yield from TraversalMixin.preorder(child)

    @staticmethod
    def postorder(root: Optional[Union[BinaryNode, GeneralNode]]) -> Iterator[Any]:
        """
        Postorder traversal: children first, then root.
        Binary: left, right, root.
        General: each child in order, then root.
        """
        if root is None:
            return
        if _is_binary(root):
            yield from TraversalMixin.postorder(root.left)
            yield from TraversalMixin.postorder(root.right)
        elif _is_general(root):
            for child in root.children:
                yield from TraversalMixin.postorder(child)
        yield root.value

    @staticmethod
    def level_order(root: Optional[Union[BinaryNode, GeneralNode]]) -> Iterator[Any]:
        """
        Level-order (BFS) traversal: nodes level by level.
        """
        if root is None:
            return
        q: deque = deque([root])
        while q:
            node = q.popleft()
            yield node.value
            if _is_binary(node):
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            elif _is_general(node):
                for child in node.children:
                    q.append(child)
