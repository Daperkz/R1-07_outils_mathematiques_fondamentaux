# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# mesh
# ==============================================================================

from __future__ import annotations

from typing import TypedDict


class AddedCube(TypedDict):
    """Enregistre les éléments de maillage créés pour un cube ajouté."""

    base_face: tuple[int, ...]
    new_verts: set[int]
    added_edges: list[tuple[int, int]]
    added_faces: list[tuple[int, ...]]


def get_cube_data(
    scene_vertices_count: int,
    scene_edges: tuple[tuple[int, int], ...],
    added_cubes: list[AddedCube],
    cube_idx: int | None,
) -> tuple[set[int], set[tuple[int, int]]]:
    """Retourne les sommets et arêtes appartenant à un cube."""
    if cube_idx is None:
        return set(), set()
    if cube_idx == 0:
        verts = set(range(scene_vertices_count))
        edges = set(scene_edges) | {(b, a) for a, b in scene_edges}
        return verts, edges
    if 1 <= cube_idx <= len(added_cubes):
        cube = added_cubes[cube_idx - 1]
        i0, i1, i2, i3 = cube["base_face"]
        verts = set(cube["base_face"]) | set(cube["new_verts"])
        base_edges = [(i0, i1), (i1, i2), (i2, i3), (i3, i0)]
        raw_edges = set(cube["added_edges"]) | set(base_edges)
        edges = raw_edges | {(b, a) for a, b in raw_edges}
        return verts, edges
    return set(), set()


def get_cube_for_face(
    added_cubes: list[AddedCube], face: tuple[int, ...]
) -> int:
    """Retourne l'indice du cube auquel appartient une face."""
    for idx in range(len(added_cubes) - 1, -1, -1):
        if any(v in added_cubes[idx]["new_verts"] for v in face):
            return idx + 1
    return 0


def add_cube_on_face(
    vertices: list[tuple[float, float, float]],
    edges: list[tuple[int, int]],
    faces: list[tuple[int, ...]],
    added_cubes: list[AddedCube],
    face_idx: int,
) -> bool:
    """Extrude un cube sur une face et met à jour le maillage en place."""
    if face_idx < 0 or face_idx >= len(faces):
        return False

    face = faces[face_idx]
    if len(face) < 4:
        return False

    pts = [vertices[i] for i in face]
    p0, p1, p2, p3 = pts[0], pts[1], pts[2], pts[3]

    s = (
        (p1[0] - p0[0]) ** 2
        + (p1[1] - p0[1]) ** 2
        + (p1[2] - p0[2]) ** 2
    ) ** 0.5
    if s <= 0.001:
        s = 2.0

    u = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    w = (p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2])
    nx = u[1] * w[2] - u[2] * w[1]
    ny = u[2] * w[0] - u[0] * w[2]
    nz = u[0] * w[1] - u[1] * w[0]
    norm = (nx * nx + ny * ny + nz * nz) ** 0.5
    if norm == 0:
        n = (0.0, 0.0, 1.0)
    else:
        n = (nx / norm, ny / norm, nz / norm)

    cx = sum(v[0] for v in vertices) / len(vertices)
    cy = sum(v[1] for v in vertices) / len(vertices)
    cz = sum(v[2] for v in vertices) / len(vertices)
    fcx = (p0[0] + p1[0] + p2[0] + p3[0]) / 4
    fcy = (p0[1] + p1[1] + p2[1] + p3[1]) / 4
    fcz = (p0[2] + p1[2] + p2[2] + p3[2]) / 4
    dot = n[0] * (fcx - cx) + n[1] * (fcy - cy) + n[2] * (fcz - cz)
    if dot < 0:
        n = (-n[0], -n[1], -n[2])

    base_idx = len(vertices)
    new_v = [
        (p0[0] + s * n[0], p0[1] + s * n[1], p0[2] + s * n[2]),
        (p1[0] + s * n[0], p1[1] + s * n[1], p1[2] + s * n[2]),
        (p2[0] + s * n[0], p2[1] + s * n[1], p2[2] + s * n[2]),
        (p3[0] + s * n[0], p3[1] + s * n[1], p3[2] + s * n[2]),
    ]
    vertices.extend(new_v)

    i0, i1, i2, i3 = face[0], face[1], face[2], face[3]
    k0, k1, k2, k3 = base_idx, base_idx + 1, base_idx + 2, base_idx + 3

    new_edges = [
        (i0, k0),
        (i1, k1),
        (i2, k2),
        (i3, k3),
        (k0, k1),
        (k1, k2),
        (k2, k3),
        (k3, k0),
    ]
    edges.extend(new_edges)

    faces.pop(face_idx)
    new_faces = [
        (k0, k1, k2, k3),
        (i0, i1, k1, k0),
        (i1, i2, k2, k1),
        (i2, i3, k3, k2),
        (i3, i0, k0, k3),
    ]
    faces.extend(new_faces)

    added_cubes.append({
        "base_face": tuple(face),
        "new_verts": set(range(base_idx, base_idx + 4)),
        "added_edges": new_edges,
        "added_faces": new_faces,
    })
    return True


def remove_cube_at_face(
    vertices: list[tuple[float, float, float]],
    edges: list[tuple[int, int]],
    faces: list[tuple[int, ...]],
    added_cubes: list[AddedCube],
    face_idx: int,
) -> bool:
    """Retire le cube choisi et ses dépendants, puis met à jour le maillage."""
    if not added_cubes:
        return False

    if face_idx < 0 or face_idx >= len(faces):
        target_cube_idx = len(added_cubes) - 1
    else:
        clicked_face = faces[face_idx]
        target_cube_idx = -1
        for idx in range(len(added_cubes) - 1, -1, -1):
            cube = added_cubes[idx]
            if any(v in cube["new_verts"] for v in clicked_face):
                target_cube_idx = idx
                break

        if target_cube_idx == -1:
            target_cube_idx = len(added_cubes) - 1

    for _ in range(len(added_cubes) - 1, target_cube_idx - 1, -1):
        cube = added_cubes.pop()
        for face in cube["added_faces"]:
            if face in faces:
                faces.remove(face)
        faces.append(cube["base_face"])
        for edge in cube["added_edges"]:
            if edge in edges:
                edges.remove(edge)
            elif (edge[1], edge[0]) in edges:
                edges.remove((edge[1], edge[0]))
        for _ in range(4):
            if vertices:
                vertices.pop()

    return True
