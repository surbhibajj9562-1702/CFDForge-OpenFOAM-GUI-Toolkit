"""
Node classes for Binary and General trees.

Uses dataclasses for clean, immutable-friendly node representation.

CFD interpretation (optional semantics):
  The tree can represent a multi-block CFD domain: each node is one block.
  Parent-child edges encode block adjacency (neighbouring blocks in the grid).
  Optional fields block_dimensions, block_index, and adjacency allow storing
  block geometry and connectivity without changing tree structure or traversal.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Tuple, Union


@dataclass
class BinaryNode:
    """
    Node for a binary tree.

    Attributes:
        value: The node's data.
        left: Left child (None if absent).
        right: Right child (None if absent).
        block_dimensions: Optional CFD: (nx, ny, nz) or [nx, ny, nz] cell counts.
        block_index: Optional CFD: global block index in the multi-block domain.
        adjacency: Optional CFD: list of adjacent block indices or identifiers.
    """

    value: Any
    left: Optional["BinaryNode"] = None
    right: Optional["BinaryNode"] = None
    block_dimensions: Optional[Tuple[int, ...]] = None
    block_index: Optional[int] = None
    adjacency: Optional[List[Any]] = None


@dataclass
class GeneralNode:
    """
    Node for a general tree (n children).

    Attributes:
        value: The node's data.
        children: List of child nodes (empty if leaf).
        block_dimensions: Optional CFD: (nx, ny, nz) or [nx, ny, nz] cell counts.
        block_index: Optional CFD: global block index in the multi-block domain.
        adjacency: Optional CFD: list of adjacent block indices or identifiers.
    """

    value: Any
    children: List["GeneralNode"] = field(default_factory=list)
    block_dimensions: Optional[Tuple[int, ...]] = None
    block_index: Optional[int] = None
    adjacency: Optional[List[Any]] = None
