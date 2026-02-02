"""
CLI interface: build tree from YAML, print tree, export to YAML.

Usage:
  tree-cli build <yaml_file>
  tree-cli print [--from-path PATH] [<yaml_file>]
  tree-cli export <yaml_file> [--output out.yaml] [--type binary|general]
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from tree_package.config import TreeConfig, TreeType
from tree_package.yaml_handler import yaml_to_tree, tree_to_yaml
from tree_package.binary_tree import BinaryTreeOperations
from tree_package.general_tree import GeneralTreeOperations
from tree_package.traversal import TraversalMixin
from tree_package.validation import validate_tree
from tree_package.exceptions import InvalidYAMLError, TreeError


def _load_yaml_file(path: Path) -> str:
    """Load YAML content from file."""
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def _save_yaml_file(path: Path, content: str) -> None:
    """Save YAML content to file."""
    path.write_text(content, encoding="utf-8")


def _get_operations(root):
    """Get appropriate operations for root type."""
    if hasattr(root, "left") and hasattr(root, "right"):
        return BinaryTreeOperations
    return GeneralTreeOperations


def cmd_build(args: argparse.Namespace) -> None:
    """Build tree from YAML and print it."""
    yaml_path = Path(args.yaml_file)
    content = _load_yaml_file(yaml_path)
    tree_type = TreeType(args.tree_type) if args.tree_type else TreeType.BINARY
    config = TreeConfig(tree_type=tree_type)
    try:
        root = yaml_to_tree(content, config=config)
    except InvalidYAMLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if root is None:
        print("(empty tree)")
        return
    try:
        validate_tree(root)
    except TreeError as e:
        print(f"Validation warning: {e}", file=sys.stderr)
    ops = _get_operations(root)
    print(ops.print_tree(root))
    print("\nTree built successfully.")


def cmd_print(args: argparse.Namespace) -> None:
    """Print tree from YAML file."""
    yaml_path = Path(args.yaml_file)
    content = _load_yaml_file(yaml_path)
    tree_type = TreeType(args.tree_type) if args.tree_type else TreeType.BINARY
    config = TreeConfig(tree_type=tree_type)
    try:
        root = yaml_to_tree(content, config=config)
    except InvalidYAMLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if root is None:
        print("(empty tree)")
        return
    ops = _get_operations(root)
    from_path = args.from_path or ""
    print(ops.print_subtree(root, from_path=from_path))


def cmd_export(args: argparse.Namespace) -> None:
    """Export tree to YAML file."""
    yaml_path = Path(args.yaml_file)
    content = _load_yaml_file(yaml_path)
    tree_type = TreeType(args.tree_type) if args.tree_type else TreeType.BINARY
    config = TreeConfig(tree_type=tree_type)
    try:
        root = yaml_to_tree(content, config=config)
    except InvalidYAMLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if root is None:
        print("(empty tree) - nothing to export")
        return
    out_path = Path(args.output) if args.output else yaml_path.with_suffix(".exported.yaml")
    yaml_str = tree_to_yaml(root, config=config)
    _save_yaml_file(out_path, yaml_str)
    print(f"Exported to {out_path}")


def cmd_traverse(args: argparse.Namespace) -> None:
    """Print tree traversal order."""
    yaml_path = Path(args.yaml_file)
    content = _load_yaml_file(yaml_path)
    tree_type = TreeType(args.tree_type) if args.tree_type else TreeType.BINARY
    config = TreeConfig(tree_type=tree_type)
    try:
        root = yaml_to_tree(content, config=config)
    except InvalidYAMLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    if root is None:
        print("(empty tree)")
        return
    order = args.order or "preorder"
    if order == "inorder":
        values = list(TraversalMixin.inorder(root))
    elif order == "preorder":
        values = list(TraversalMixin.preorder(root))
    elif order == "postorder":
        values = list(TraversalMixin.postorder(root))
    elif order == "level":
        values = list(TraversalMixin.level_order(root))
    else:
        print(f"Unknown order: {order}", file=sys.stderr)
        sys.exit(1)
    print(" ".join(str(v) for v in values))


def main() -> int:
    """Entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="tree-cli",
        description="CFD-FOSSEE Tree Package CLI: build, print, and export trees from YAML.",
    )
    parser.add_argument(
        "--type",
        dest="tree_type",
        choices=["binary", "general"],
        default="binary",
        help="Tree type: binary or general (default: binary)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = subparsers.add_parser("build", help="Build tree from YAML and print")
    p_build.add_argument("yaml_file", help="Path to YAML file")
    p_build.set_defaults(func=cmd_build)

    # print
    p_print = subparsers.add_parser("print", help="Print tree from YAML")
    p_print.add_argument("yaml_file", help="Path to YAML file")
    p_print.add_argument("--from-path", default="", help="Print subtree from path (L/R for binary, 0,1 for general)")
    p_print.set_defaults(func=cmd_print)

    # export
    p_export = subparsers.add_parser("export", help="Export tree to YAML")
    p_export.add_argument("yaml_file", help="Path to YAML file")
    p_export.add_argument("--output", "-o", help="Output file path")
    p_export.set_defaults(func=cmd_export)

    # traverse (bonus)
    p_traverse = subparsers.add_parser("traverse", help="Print traversal order")
    p_traverse.add_argument("yaml_file", help="Path to YAML file")
    p_traverse.add_argument(
        "--order",
        choices=["inorder", "preorder", "postorder", "level"],
        default="preorder",
        help="Traversal order (default: preorder)",
    )
    p_traverse.set_defaults(func=cmd_traverse)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
