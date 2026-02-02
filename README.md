# CFD-FOSSEE (OpenFOAM GUI) 

This project consists of two independent parts (1) a Python tree-based configuration package with YAML and CLI support, and (2) a Blender addon for visual multi-block geometry construction. The intent is to reduce manual effort in defining structured configurations and geometries, with high-level relevance to OpenFOAM GUI workflows (e.g. hierarchical solver/block configuration and multi-block mesh construction).

---

## PROJECT STRUCTURE

```
FOSSEE/
├── Task1_Python_Tree_Package/
│   ├── tree_package/           # Python package (binary/general tree, YAML, CLI)
│   ├── tests/                  # Unit tests (pytest)
│   ├── sample_binary.yaml
│   ├── sample_general.yaml
│   ├── sample_cfd.yaml
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── README.md
├── Task2_Blender_Addon/
│   ├── addon.py                # Single-file Blender addon
│   ├── README.md
│   └── screenshots/
├── SOP.txt                     # Standard Operating Procedure (evaluator reference)
├── Resume.pdf                  # Candidate resume (add your file here)
└── README.md
```

---

## TASK 1: PYTHON TREE PACKAGE

**Location:** `Task1_Python_Tree_Package/`

### Feature set (screening requirements)

- **Binary Tree** implementation using a **Node class** (`BinaryNode` in `node.py`).
- **Helper functions** (via `BinaryTreeOperations` and module-level helpers):
  - **Create new tree:** `create_binary_tree(root_value)`
  - **Add node** to existing tree (path-based): `BinaryTreeOperations.add_node_by_path(root, path, value, side)` with `side` `"L"` or `"R"`
  - **Delete node:** `BinaryTreeOperations.delete_node(root, path)` — returns `(new_root, deleted_node)`
  - **Delete entire tree:** `BinaryTreeOperations.delete_tree(root)` — clears tree in place
  - **Print entire tree:** `BinaryTreeOperations.print_tree(root)` — pretty-format multiline string
  - **Print subtree / range:** `BinaryTreeOperations.print_subtree(root, from_path="")` — prints subtree at path, or full tree if `from_path` is empty
  - **Edit node value:** `BinaryTreeOperations.edit_node_value(root, path, value)`
- **YAML integration:**
  - **YAML → tree:** `yaml_to_tree(yaml_str, config)` — parses YAML into binary or general tree
  - **Tree → YAML:** `tree_to_yaml(root, config)` — serializes tree to YAML string
  - **Graceful handling of missing children:** `left`/`right` (binary) and `children` (general) may be omitted or null; missing keys are treated as no child
  - **Clear error handling:** `InvalidYAMLError` on malformed YAML or missing required `value` key; path/node errors raise `InvalidPathError`, `NodeNotFoundError`
- **Bonus — General tree support:** General tree with **any number of children** (`GeneralNode`, `GeneralTreeOperations`), path format `"0"`, `"0,1"` or `"0.1"` for child indices. YAML format uses `children: [...]`.

### Node structure and optional CFD metadata

Nodes have a required `value` field. Optional CFD-aware metadata (ignored when absent for backward compatibility): `block_dimensions` (e.g. `[nx, ny, nz]`), `block_index`, `adjacency`. Trees can represent hierarchical CFD configurations (e.g. block connectivity) aligned with OpenFOAM dictionary-style nesting.

### CLI usage (as per SOP)

```bash
cd Task1_Python_Tree_Package
pip install -e .
pip install pytest   # for tests

tree-cli build sample_binary.yaml
tree-cli print sample_binary.yaml
tree-cli print sample_binary.yaml --from-path L
tree-cli export sample_binary.yaml --output out.yaml
tree-cli traverse sample_binary.yaml --order preorder
```

General tree (bonus):

```bash
tree-cli --type general build sample_general.yaml
tree-cli --type general export sample_general.yaml --output out_general.yaml
```

**Example output** (`tree-cli build sample_binary.yaml`; UTF-8 terminal):

```
└── 1
    L: ├── 2
    │   L: ├── 4
    │   R: └── 5
    R: └── 3
        L: ├── 6
        R: └── 7

Tree built successfully.
```

### Run tests (Task 1)

```bash
cd Task1_Python_Tree_Package
pip install -e ".[dev]"
pytest
```

**45 tests** cover: create tree, add/delete/edit node, delete tree, print tree/subtree, traversals (inorder, preorder, postorder, level-order), YAML parse/serialize, graceful missing children, optional CFD fields, validation (cycle detection).

---

## TASK 2: BLENDER ADDON

**Location:** `Task2_Blender_Addon/`  
**Requirements:** Blender 3.0+

### Install (as per SOP)

1. Blender → **Edit → Preferences → Add-ons**
2. **Install...** → select `addon.py` from `Task2_Blender_Addon`
3. Enable **"CFD-FOSSEE Cube Tools"**
4. Panel: **View3D → Sidebar (N) → CFD-FOSSEE** tab

### Feature set (screening requirements)

**Feature set 1 — Cube distribution and management**

- **UI Panel** with **input box for natural number N** (property **N**, range 1–19). Panel label: "N (natural number, < 20):".
- **Strict enforcement of N < 20:** N must be 1–19; values outside range are invalid.
- **Popup error when N ≥ 20:** If user clicks "Distribute Cubes" with N ≥ 20 (or N < 1), a **popup dialog** appears with message "N must be less than 20 (natural number). Got N = &lt;value&gt;." and "Valid range: 1 to 19." Error is also reported in the header.
- **Button "Distribute Cubes":** Distributes **N cubes** of **size = 1 unit** into an **m × n grid** (m, n chosen so m×n ≥ N with minimal difference).
- **Optional separate collection:** Checkbox "Use Collection" places cubes in collection **"CFD-FOSSEE Cubes"**.
- **Button "Delete Selected Cubes":** Deletes selected CFD-FOSSEE cubes (confirmation dialog).
- **Algorithm preventing overlap:** Cube positions are chosen so new cubes do not overlap existing objects in the scene; grid is shifted as needed.

**Feature set 2 — Mesh merge**

- **Button "Merge Meshes":** Merges selected meshes.
- **Validation:** At least one **full face** must be shared between some pair of selected meshes (tolerance-based face matching). Invalid merges are prevented.
- **Merge common vertices:** Vertices within numerical tolerance are welded after join.
- **Remove common/internal faces:** Duplicate/internal faces (from shared boundaries) are removed so the result is a single clean mesh named **"CFD-FOSSEE_Merged"**.
- **Clear user feedback for failure cases:** If no full face is shared, the addon reports a clear reason:
  - **Gap** — meshes do not touch within tolerance
  - **Edge-touch** — meshes touch only at an edge; full face contact required
  - **Corner-touch** — meshes touch only at a corner; full face contact required

Output is **visual in the Blender viewport** only; no OpenFOAM file export.

---

## SETUP & USAGE SUMMARY

| Item               | Instructions                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Python**         | 3.8+; PyYAML ≥ 6.0 (installed with Task 1 package)                                                                  |
| **Task 1 install** | `cd Task1_Python_Tree_Package` then `pip install -e .`                                                              |
| **Task 1 CLI**     | `tree-cli build/print/export/traverse &lt;yaml_file&gt;` (see above)                                                |
| **Task 1 tests**   | `cd Task1_Python_Tree_Package` then `pytest`                                                                        |
| **Task 2 addon**   | Install `addon.py` in Blender 3.0+ and enable "CFD-FOSSEE Cube Tools"; use panel in View3D Sidebar (N) → CFD-FOSSEE |

---

## DESIGN NOTES

- **Stateless CLI:** Each `tree-cli` command reads from the given YAML file and prints or writes output; no persistent in-memory tree between invocations.
- **Backward-compatible YAML:** CFD fields are optional; YAML files without them work unchanged.
- **Numerical tolerance (Blender merge):** Shared-face detection uses a small epsilon to handle floating-point differences; merge fails with clear messages when meshes only touch at edge or corner.
- **Strict merge constraints:** Requiring at least one full shared face ensures a watertight single mesh; edge/corner-only contact is not merged.

---

## LIMITATIONS & FUTURE WORK

- No direct OpenFOAM dictionary export (e.g. `blockMeshDict`) from either task.
- Possible extensions: export tree or block layout to `blockMeshDict`, solver/parameter GUI backed by tree or YAML, Blender → STL/OpenFOAM export.

---

## EVALUATOR NOTES (from SOP)

- **Task 1:** Run `pytest` from `Task1_Python_Tree_Package/`.
- **Task 2:** Install addon in Blender and test in 3D Viewport (distribute cubes, delete cubes, merge two cubes with a shared face).
- All code has docstrings and type hints; no placeholders or TODOs; everything is runnable.

---

## LICENSE

- Task 1: MIT
- Task 2: GPL v2+ (see header in `addon.py`)
