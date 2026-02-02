# ##### BEGIN GPL LICENSE BLOCK #####
#
#  CFD-FOSSEE Cube Addon - Blender addon for cube distribution and mesh merge
#  Copyright (C) 2024 CFD-FOSSEE Screening
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "CFD-FOSSEE Cube Tools",
    "author": "CFD-FOSSEE Screening",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > CFD-FOSSEE",
    "description": "Distribute cubes in grid, manage cubes, and merge meshes with common faces",
    "category": "3D View",
}

import bpy
import bmesh
import math
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty, BoolProperty


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ADDON_NAME = "cfd_fossee_cube_tools"
COLLECTION_NAME = "CFD-FOSSEE Cubes"
MAX_N = 20
DEFAULT_GRID_SPACING = 1.5
# Numerical tolerance for shared-face detection (avoids false negatives from float drift)
FACE_EPSILON = 1e-6
# Last merge failure reason (set when merge fails; used for operator report)
_last_merge_failure_reason = ""


def log(msg: str) -> None:
    """Log operation to Blender console for debugging."""
    print(f"[CFD-FOSSEE] {msg}")


# ---------------------------------------------------------------------------
# Cube Distribution
# ---------------------------------------------------------------------------
def get_collection(name: str):
    """Get or create a collection by name."""
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def get_existing_bounds() -> list:
    """
    Get bounding boxes of all mesh objects in scene (excluding CFD-FOSSEE Cubes).
    Returns list of (min_corner, max_corner) as Vector tuples.
    """
    bounds = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if obj.name.startswith("CFD-FOSSEE_Cube"):
            continue
        if obj.mode != "OBJECT":
            continue
        world_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if not world_verts:
            continue
        xs = [v.x for v in world_verts]
        ys = [v.y for v in world_verts]
        zs = [v.z for v in world_verts]
        mn = Vector((min(xs), min(ys), min(zs)))
        mx = Vector((max(xs), max(ys), max(zs)))
        bounds.append((mn, mx))
    return bounds


def overlaps_existing(cube_min: Vector, cube_max: Vector, existing: list, margin: float = 0.01) -> bool:
    """Check if cube bounds overlap any existing object bounds."""
    for (em, eM) in existing:
        if (cube_min.x - margin <= eM.x and cube_max.x + margin >= em.x and
            cube_min.y - margin <= eM.y and cube_max.y + margin >= em.y and
            cube_min.z - margin <= eM.z and cube_max.z + margin >= em.z):
            return True
    return False


def compute_grid_shape(n: int) -> tuple:
    """Compute m, n for m×n grid with m >= n, m * n >= n, minimal difference."""
    m = int(math.ceil(math.sqrt(n)))
    n_cols = m
    n_rows = (n + m - 1) // m
    return n_rows, n_cols


def distribute_cubes(context, n: int, spacing: float, use_collection: bool) -> set:
    """
    Create N cubes of size 1, arrange in 2D grid, avoid overlap with existing objects.
    Returns set of created object names for undo/selection.
    """
    n_rows, n_cols = compute_grid_shape(n)
    created = set()
    existing_bounds = get_existing_bounds()
    coll = get_collection(COLLECTION_NAME) if use_collection else context.scene.collection

    # Find a clear starting position (top-right of all existing objects)
    base_x, base_y = 0.0, 0.0
    if existing_bounds:
        all_max_x = max(mx.x for _, mx in existing_bounds)
        all_max_y = max(mx.y for _, mx in existing_bounds)
        base_x = all_max_x + spacing
        base_y = all_max_y + spacing

    cube_idx = 0
    for row in range(n_rows):
        for col in range(n_cols):
            if cube_idx >= n:
                break
            x = base_x + col * spacing
            y = base_y + row * spacing
            z = 0.0

            cube_min = Vector((x - 0.5, y - 0.5, z - 0.5))
            cube_max = Vector((x + 0.5, y + 0.5, z + 0.5))

            # If overlaps, shift further
            while overlaps_existing(cube_min, cube_max, existing_bounds):
                base_x += spacing
                base_y += spacing
                x = base_x + col * spacing
                y = base_y + row * spacing
                cube_min = Vector((x - 0.5, y - 0.5, z - 0.5))
                cube_max = Vector((x + 0.5, y + 0.5, z + 0.5))
                existing_bounds = get_existing_bounds()

            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
            obj = context.active_object
            obj.name = f"CFD-FOSSEE_Cube_{cube_idx:03d}"

            if use_collection:
                if obj.name in context.scene.collection.objects:
                    context.scene.collection.objects.unlink(obj)
                coll.objects.link(obj)

            created.add(obj.name)
            existing_bounds.append((cube_min, cube_max))
            cube_idx += 1

    return created


# ---------------------------------------------------------------------------
# Mesh Merge with Common Face Detection (CFD preprocessing: multi-block
# geometry with shared faces is common; merge ensures watertight mesh.)
# ---------------------------------------------------------------------------
def get_face_center_edges(face) -> tuple:
    """
    Get a hashable representation of a face for comparison.
    Uses sorted tuple of vertex coordinates (world-space, rounded for stability).
    """
    verts = [face.verts[i].co.copy() for i in range(len(face.verts))]
    verts_sorted = sorted(
        verts,
        key=lambda v: (round(v.x, 5), round(v.y, 5), round(v.z, 5))
    )
    key = tuple(
        (round(v.x, 5), round(v.y, 5), round(v.z, 5))
        for v in verts_sorted
    )
    return key


def get_face_key_from_bmesh(bm, face) -> tuple:
    """Get canonical key for a bmesh face (rounded for duplicate detection)."""
    verts = []
    for loop in face.loops:
        v = loop.vert.co.copy()
        verts.append((round(v.x, 5), round(v.y, 5), round(v.z, 5)))
    verts.sort()
    return tuple(verts)


def mesh_faces_match(f1_verts, f2_verts, epsilon: float = FACE_EPSILON) -> bool:
    """
    Check if two faces match: same number of vertices, each vertex within epsilon.
    Uses numerical tolerance to avoid false negatives from floating-point offsets.
    f1_verts, f2_verts: list of (x,y,z) (or list-like); order normalized by caller.
    """
    if len(f1_verts) != len(f2_verts):
        return False
    n = len(f1_verts)
    for offset in range(n):
        match = True
        for i in range(n):
            a = f1_verts[i]
            b = f2_verts[(i + offset) % n]
            if (abs(a[0] - b[0]) > epsilon or
                abs(a[1] - b[1]) > epsilon or
                abs(a[2] - b[2]) > epsilon):
                match = False
                break
        if match:
            return True
    return False


def get_face_world_verts(obj, face) -> list:
    """Get face vertex coordinates in world space as list of (x,y,z)."""
    return [
        (obj.matrix_world @ obj.data.vertices[v].co)[:]
        for v in face.vertices
    ]


def find_common_faces(obj_a, obj_b, epsilon: float = FACE_EPSILON) -> list:
    """
    Find pairs of faces (from obj_a and obj_b) that are shared (same geometry).
    Uses raw coordinates with epsilon comparison to avoid false negatives from
    floating-point rounding. Vertices within epsilon are treated as coincident.
    Returns list of (face_index_a, face_index_b).
    """
    if obj_a.type != "MESH" or obj_b.type != "MESH":
        return []

    mesh_a = obj_a.data
    mesh_b = obj_b.data
    common = []

    for i, fa in enumerate(mesh_a.polygons):
        verts_a = get_face_world_verts(obj_a, fa)
        # Canonical order by (x,y,z) so matching faces compare equal
        verts_a_sorted = sorted(verts_a, key=lambda v: (v[0], v[1], v[2]))

        for j, fb in enumerate(mesh_b.polygons):
            verts_b = get_face_world_verts(obj_b, fb)
            verts_b_sorted = sorted(verts_b, key=lambda v: (v[0], v[1], v[2]))

            if mesh_faces_match(verts_a_sorted, verts_b_sorted, epsilon):
                common.append((i, j))
                break

    return common


def _mesh_vertex_positions(obj) -> list:
    """Return list of world-space (x,y,z) for all vertices of a mesh object."""
    if obj.type != "MESH" or not obj.data.vertices:
        return []
    return [(obj.matrix_world @ v.co)[:] for v in obj.data.vertices]


def _classify_merge_failure_reason(obj_a, obj_b, epsilon: float = FACE_EPSILON) -> str:
    """
    Classify why merge failed: no full face shared.
    Returns one of: "gap", "edge-touch", "corner-touch".
    """
    verts_a = _mesh_vertex_positions(obj_a)
    verts_b = _mesh_vertex_positions(obj_b)
    if not verts_a or not verts_b:
        return "gap"

    # Count vertex pairs within epsilon (touching)
    touch_count = 0
    min_dist = float("inf")
    for va in verts_a:
        for vb in verts_b:
            d = (Vector(va) - Vector(vb)).length
            min_dist = min(min_dist, d)
            if d <= epsilon:
                touch_count += 1

    if min_dist > epsilon:
        return "gap"
    if touch_count >= 2:
        return "edge-touch"
    return "corner-touch"


def merge_meshes_with_common_faces(context, objects: list) -> bool:
    """
    Merge selected meshes if they share at least one common face.
    Uses bmesh for robust vertex merge and removes internal faces.
    Returns True on success. On failure, logs a clear reason (gap / edge-touch / corner-touch).
    """
    if len(objects) < 2:
        log("Merge failed: need at least 2 meshes selected")
        return False

    # Check pairwise for at least one common face (within numerical tolerance)
    has_common = False
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            if find_common_faces(objects[i], objects[j]):
                has_common = True
                break
        if has_common:
            break

    if not has_common:
        # Classify why: gap, edge-touch, or corner-touch (no full face contact)
        global _last_merge_failure_reason
        reason = "gap"
        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                r = _classify_merge_failure_reason(objects[i], objects[j])
                if r != "gap":
                    reason = r
                    break
            if reason != "gap":
                break
        if reason == "gap":
            _last_merge_failure_reason = "No common face (gap between meshes)"
            log("Merge failed: no common face (gap between selected meshes)")
        elif reason == "edge-touch":
            _last_merge_failure_reason = "Touch only at edge; full face contact required"
            log("Merge failed: meshes touch only at an edge; full face contact required")
        else:
            _last_merge_failure_reason = "Touch only at corner; full face contact required"
            log("Merge failed: meshes touch only at a corner; full face contact required")
        return False

    # Join all selected meshes into one object
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    merged = context.active_object
    merged.name = "CFD-FOSSEE_Merged"

    # Weld vertices that are within tolerance (clean shared boundaries)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=FACE_EPSILON)
    bpy.ops.mesh.select_all(action="DESELECT")

    # Remove internal/duplicate faces (shared faces become double-sided)
    bm = bmesh.from_edit_mesh(merged.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    seen = set()
    to_remove = []
    for f in bm.faces:
        verts_key = tuple(sorted(((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5))
                                 for v in f.verts)))
        if verts_key in seen or f.calc_area() < 1e-10:
            to_remove.append(f)
        else:
            seen.add(verts_key)
    for f in to_remove:
        bm.faces.remove(f)
    bmesh.update_edit_mesh(merged.data)
    bpy.ops.object.mode_set(mode="OBJECT")

    log(f"Merged {len(objects)} meshes into {merged.name}")
    return True


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------
class CFD_FOSSEE_OT_ErrorPopupN(bpy.types.Operator):
    """Show popup when N is invalid (N >= 20 or N < 1)"""
    bl_idname = "cfd_fossee.error_popup_n"
    bl_label = "Invalid N"
    bl_options = {"INTERNAL"}

    message: bpy.props.StringProperty(name="Message", default="N must be less than 20 (natural number).")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.message)
        layout.label(text="Valid range: 1 to 19.")

    def execute(self, context):
        return {"FINISHED"}


class CFD_FOSSEE_OT_DistributeCubes(bpy.types.Operator):
    """Distribute N cubes in a 2D grid (size 1, no overlap). N must be < 20."""
    bl_idname = "cfd_fossee.distribute_cubes"
    bl_label = "Distribute Cubes"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        props = context.scene.cfd_fossee_props
        n = props.cube_count
        if n < 1 or n >= MAX_N:
            bpy.ops.cfd_fossee.error_popup_n(
                "INVOKE_DEFAULT",
                message=f"N must be less than 20 (natural number). Got N = {n}.",
            )
            self.report({"ERROR"}, f"N must be 1 to {MAX_N - 1} (got {n})")
            return {"CANCELLED"}
        return self.execute(context)

    def execute(self, context):
        props = context.scene.cfd_fossee_props
        n = props.cube_count
        if n < 1 or n >= MAX_N:
            self.report({"ERROR"}, f"N must be 1 to {MAX_N - 1} (got {n})")
            return {"CANCELLED"}
        spacing = props.grid_spacing
        use_coll = props.use_collection
        try:
            created = distribute_cubes(context, n, spacing, use_coll)
            self.report({"INFO"}, f"Created {len(created)} cubes")
            log(f"Distribute: created {len(created)} cubes")
            return {"FINISHED"}
        except Exception as e:
            log(f"Distribute error: {e}")
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}


class CFD_FOSSEE_OT_DeleteSelectedCubes(bpy.types.Operator):
    """Delete selected CFD-FOSSEE cubes with confirmation"""
    bl_idname = "cfd_fossee.delete_selected_cubes"
    bl_label = "Delete Selected Cubes"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        cube_objs = [
            o for o in context.selected_objects
            if o.type == "MESH" and o.name.startswith("CFD-FOSSEE_Cube")
        ]
        if not cube_objs:
            self.report({"WARNING"}, "No CFD-FOSSEE cubes selected")
            return {"CANCELLED"}
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        cube_objs = [
            o for o in context.selected_objects
            if o.type == "MESH" and o.name.startswith("CFD-FOSSEE_Cube")
        ]
        for obj in cube_objs:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({"INFO"}, f"Deleted {len(cube_objs)} cubes")
        log(f"Delete: removed {len(cube_objs)} cubes")
        return {"FINISHED"}


class CFD_FOSSEE_OT_MergeMeshes(bpy.types.Operator):
    """Merge selected meshes if they share at least one common face"""
    bl_idname = "cfd_fossee.merge_meshes"
    bl_label = "Merge Meshes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global _last_merge_failure_reason
        _last_merge_failure_reason = ""
        objs = [o for o in context.selected_objects if o.type == "MESH"]
        if len(objs) < 2:
            self.report({"ERROR"}, "Select at least 2 meshes to merge")
            return {"CANCELLED"}
        if merge_meshes_with_common_faces(context, objs):
            self.report({"INFO"}, "Meshes merged successfully")
            return {"FINISHED"}
        msg = _last_merge_failure_reason or "No common faces between selected meshes"
        self.report({"ERROR"}, msg)
        return {"CANCELLED"}


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------
class CFD_FOSSEE_Properties(bpy.types.PropertyGroup):
    cube_count: IntProperty(
        name="N",
        description="Natural number N < 20: number of cubes to distribute (1-19)",
        default=9,
        min=1,
        max=MAX_N - 1,
        soft_min=1,
        soft_max=19,
    )
    grid_spacing: FloatProperty(
        name="Grid Spacing",
        description="Spacing between cubes",
        default=DEFAULT_GRID_SPACING,
        min=1.01,
        max=10.0,
        soft_min=1.1,
        step=1,
    )
    use_collection: BoolProperty(
        name="Use Collection",
        description="Place cubes in CFD-FOSSEE Cubes collection",
        default=True,
    )
    status_message: bpy.props.StringProperty(
        name="Status",
        description="Status message",
        default="",
    )


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------
class CFD_FOSSEE_PT_Panel(bpy.types.Panel):
    bl_label = "CFD-FOSSEE Cube Tools"
    bl_idname = "CFD_FOSSEE_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CFD-FOSSEE"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cfd_fossee_props

        box = layout.box()
        box.label(text="Cube Distribution", icon="MESH_CUBE")
        row = box.row()
        row.label(text="N (natural number, < 20):")
        row = box.row()
        row.prop(props, "cube_count")
        row = box.row()
        row.prop(props, "grid_spacing")
        row = box.row()
        row.prop(props, "use_collection")
        row = box.row()
        row.scale_y = 1.2
        row.operator("cfd_fossee.distribute_cubes", text="Distribute Cubes", icon="ADD")
        if props.cube_count >= MAX_N or props.cube_count < 1:
            row = box.row()
            row.alert = True
            row.label(text=f"N must be 1-{MAX_N - 1}", icon="ERROR")

        box = layout.box()
        box.label(text="Cube Management", icon="TRASH")
        row = box.row()
        row.scale_y = 1.2
        row.operator("cfd_fossee.delete_selected_cubes", text="Delete Selected Cubes", icon="X")

        box = layout.box()
        box.label(text="Mesh Operations", icon="MOD_BOOLEAN")
        row = box.row()
        row.label(text="Select 2+ meshes with shared face")
        row = box.row()
        row.scale_y = 1.2
        row.operator("cfd_fossee.merge_meshes", text="Merge Meshes", icon="AUTOMERGE_ON")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
CLASSES = [
    CFD_FOSSEE_Properties,
    CFD_FOSSEE_OT_ErrorPopupN,
    CFD_FOSSEE_OT_DistributeCubes,
    CFD_FOSSEE_OT_DeleteSelectedCubes,
    CFD_FOSSEE_OT_MergeMeshes,
    CFD_FOSSEE_PT_Panel,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cfd_fossee_props = bpy.props.PointerProperty(type=CFD_FOSSEE_Properties)
    log("CFD-FOSSEE Cube Tools registered")


def unregister():
    del bpy.types.Scene.cfd_fossee_props
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    log("CFD-FOSSEE Cube Tools unregistered")


if __name__ == "__main__":
    register()
