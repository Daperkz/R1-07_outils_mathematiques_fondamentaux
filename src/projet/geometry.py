# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# geometry
# ==============================================================================

from __future__ import annotations


def distance_to_segment(
    point: tuple[int, int],
    start: tuple[int, int],
    end: tuple[int, int],
) -> float:
    """Calcule la distance entre un point 2D et un segment."""
    px, py = point
    ax, ay = start
    bx, by = end
    dx = bx - ax
    dy = by - ay
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(
        0.0,
        min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_squared),
    )
    projected_x = ax + t * dx
    projected_y = ay + t * dy
    return ((px - projected_x) ** 2 + (py - projected_y) ** 2) ** 0.5


def determinant_2d(
    a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]
) -> int:
    """Calcule le déterminant 2x2 des vecteurs AB et AC."""
    ab_x: int = b[0] - a[0]
    ab_y: int = b[1] - a[1]
    ac_x: int = c[0] - a[0]
    ac_y: int = c[1] - a[1]
    return ab_x * ac_y - ab_y * ac_x


def is_face_visible(polygon: list[tuple[int, int]]) -> bool:
    """Renvoie True si la face projetée est tournée vers la caméra."""
    if len(polygon) < 3:
        return False
    return determinant_2d(polygon[0], polygon[1], polygon[2]) > 0


def polygon_area(polygon: list[tuple[int, int]]) -> float:
    """Calcule l'aire d'un polygone 2D avec la formule du lacet."""
    n: int = len(polygon)
    if n < 3:
        return 0.0

    somme: int = 0
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        somme += x1 * y2 - x2 * y1
    return abs(somme) / 2


def is_point_inside(
    point: tuple[int, int], polygon: list[tuple[int, int]]
) -> bool:
    """Teste si un point est dans le polygone par lancer de rayon."""
    x, y = point
    n: int = len(polygon)
    interieur: bool = False

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            x_croisement: float = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_croisement:
                interieur = not interieur
    return interieur


def solve_gauss(
    a: list[list[float]], b: list[float], tolerance: float = 1e-12
) -> list[float]:
    """Résout A * x = b par le pivot de Gauss avec pivot partiel."""
    n: int = len(a)
    m: list[list[float]] = [list(a[i]) + [b[i]] for i in range(n)]

    for k in range(n):
        meilleure: int = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[meilleure][k]) <= tolerance:
            raise ValueError("systeme singulier ou mal pose")
        m[k], m[meilleure] = m[meilleure], m[k]

        for i in range(k + 1, n):
            facteur: float = m[i][k] / m[k][k]
            for j in range(k, n + 1):
                m[i][j] = m[i][j] - facteur * m[k][j]

    x: list[float] = [0.0] * n
    for i in range(n - 1, -1, -1):
        somme: float = m[i][n]
        for j in range(i + 1, n):
            somme = somme - m[i][j] * x[j]
        x[i] = somme / m[i][i]
    return x


def intersect_ray_face(
    mouse_pos: tuple[int, int],
    width: int,
    height: int,
    focal_length: float,
    camera_distance: float,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> tuple[float, float, float] | None:
    """Calcule les coordonnées 3D (x, y, z) du point cliqué sur une face."""
    rx: float = (mouse_pos[0] - width / 2) / focal_length
    ry: float = (height / 2 - mouse_pos[1]) / focal_length

    ab: tuple[float, float, float] = (
        b[0] - a[0],
        b[1] - a[1],
        b[2] - a[2],
    )
    ac: tuple[float, float, float] = (
        c[0] - a[0],
        c[1] - a[1],
        c[2] - a[2],
    )

    nx: float = ab[1] * ac[2] - ab[2] * ac[1]
    ny: float = ab[2] * ac[0] - ab[0] * ac[2]
    nz: float = ab[0] * ac[1] - ab[1] * ac[0]
    d: float = nx * a[0] + ny * a[1] + nz * a[2]

    systeme: list[list[float]] = [
        [1.0, 0.0, -rx],
        [0.0, 1.0, -ry],
        [nx, ny, nz],
    ]
    second_membre: list[float] = [
        rx * camera_distance,
        ry * camera_distance,
        d,
    ]

    try:
        x, y, z = solve_gauss(systeme, second_membre)
    except ValueError:
        return None
    return x, y, z
