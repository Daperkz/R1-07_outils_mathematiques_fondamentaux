# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# parser
# ==============================================================================

from __future__ import annotations

from .matrix import Matrix


class Scene:
    """Stocke le nom, les sommets, les arêtes et les faces d'un objet 3D."""

    def __init__(
        self,
        name: str,
        vertices: tuple[tuple[float, float, float], ...],
        edges: tuple[tuple[int, int], ...],
        faces: tuple[tuple[int, ...], ...],
    ) -> None:
        self.name: str = name
        self.vertices: tuple[tuple[float, float, float], ...] = vertices
        self.edges: tuple[tuple[int, int], ...] = edges
        self.faces: tuple[tuple[int, ...], ...] = faces


def _apply_matrix(
    vertices: list[tuple[float, float, float]], transform: Matrix
) -> list[tuple[float, float, float]]:
    """Multiplie chaque sommet 3D de la liste par une matrice 3x3."""
    result: list[tuple[float, float, float]] = []
    for x, y, z in vertices:
        col: Matrix = transform @ Matrix([[x], [y], [z]])
        result.append((col[0][0], col[1][0], col[2][0]))
    return result


def load_scene(filepath: str) -> Scene:
    """Lit un fichier .txt et construit l'objet 3D correspondant."""
    name: str = filepath
    vertices: list[tuple[float, float, float]] = []
    edges: list[tuple[int, int]] = []
    faces: list[tuple[int, ...]] = []

    with open(filepath, "r", encoding="utf-8") as file:
        for raw_line in file:
            line: str = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts: list[str] = line.split()
            cmd: str = parts[0].upper()

            if cmd == "NAME":
                name = " ".join(parts[1:])
            elif cmd == "VERTEX":
                vertices.append(
                    (float(parts[1]), float(parts[2]), float(parts[3]))
                )
            elif cmd == "EDGE":
                edges.append((int(parts[1]), int(parts[2])))
            elif cmd == "FACE":
                faces.append(tuple(int(i) for i in parts[1:]))
            elif cmd == "SCALE":
                s: float = float(parts[1])
                scale_mat: Matrix = Matrix([
                    [s, 0.0, 0.0],
                    [0.0, s, 0.0],
                    [0.0, 0.0, s],
                ])
                vertices = _apply_matrix(vertices, scale_mat)
            elif cmd == "ROTATE_X":
                vertices = _apply_matrix(
                    vertices, Matrix.rotation_x(float(parts[1]))
                )
            elif cmd == "ROTATE_Y":
                vertices = _apply_matrix(
                    vertices, Matrix.rotation_y(float(parts[1]))
                )
            elif cmd == "ROTATE_Z":
                vertices = _apply_matrix(
                    vertices, Matrix.rotation_z(float(parts[1]))
                )
            elif cmd == "TRANSLATE":
                tx, ty, tz = float(parts[1]), float(parts[2]), float(parts[3])
                vertices = [(x + tx, y + ty, z + tz) for x, y, z in vertices]

    return Scene(
        name=name,
        vertices=tuple(vertices),
        edges=tuple(edges),
        faces=tuple(faces),
    )
