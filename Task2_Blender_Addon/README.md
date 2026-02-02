# CFD-FOSSEE Cube Tools - Blender Addon

Blender addon for cube distribution in a 2D grid, cube management, and mesh merging with common-face detection.

## Installation

1. In Blender: **Edit > Preferences > Add-ons**
2. Click **Install...** and select `addon.py`
3. Enable "CFD-FOSSEE Cube Tools"
4. Find the panel in **View3D > Sidebar (N) > CFD-FOSSEE** tab

## Requirements

- Blender 3.0+
- bpy, bmesh (included with Blender)

## Features

### Cube Distribution

- **N** (1–19): Number of cubes
- **Grid Spacing**: Distance between cube centers (default 1.5)
- **Use Collection**: Place cubes in "CFD-FOSSEE Cubes" collection
- **Distribute Cubes**: Creates N cubes (size 1) in m×n grid, avoids overlap with existing objects

### Cube Management

- **Delete Selected Cubes**: Removes selected CFD-FOSSEE cubes with confirmation popup

### Mesh Operations

- **Merge Meshes**: Select 2+ meshes that share at least one common face
  - Merges vertices, removes internal/duplicate faces
  - Output: single clean mesh named "CFD-FOSSEE_Merged"

### Bonus Features

- Visual feedback (status messages in UI)
- Undo support (REGISTER, UNDO on all operators)
- Invalid N highlighted in red with error icon
- Optional grid spacing control
- Operations logged to Blender console (Window > Toggle System Console)

## Usage

1. **Distribute Cubes**: Set N (1–19), optionally adjust spacing, click "Distribute Cubes"
2. **Delete Cubes**: Select cubes, click "Delete Selected Cubes", confirm
3. **Merge**: Create two adjacent cubes (e.g. with shared face), select both, click "Merge Meshes"

## Testing Merge

1. Distribute 2 cubes
2. Move one cube so it touches the other (shared face)
3. Select both cubes
4. Click "Merge Meshes"
