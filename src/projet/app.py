# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# app
# ==============================================================================

from __future__ import annotations

import pygame as pg

from .geometry import (
    intersect_ray_face,
    is_face_visible,
    is_point_inside,
    polygon_area,
)
from .matrix import Matrix
from .parser import Scene, load_scene
from .window import HEIGHT, WIDTH, Window


SCENE: Scene = load_scene("scenes/cube.txt")
VERTICES = SCENE.vertices
EDGES = SCENE.edges
FACES = SCENE.faces


class App:
    def __init__(self) -> None:
        self.angles: list[float] = [0.0, 0.0, 0.0]
        self.camera_distance: float = 4.0
        self._rotated_vertices: list[tuple[float, float, float]] = list(
            VERTICES
        )
        self._projected_vertices: list[tuple[int, int] | None] = []

    def _project(self, point: Matrix) -> tuple[int, int] | None:
        depth: float = point[2][0] + self.camera_distance
        if depth <= 0.1:
            return None

        focal_length: float = HEIGHT * 0.9
        x: float = WIDTH / 2 + point[0][0] * focal_length / depth
        y: float = HEIGHT / 2 - point[1][0] * focal_length / depth
        return round(x), round(y)

    def _handle_click(self, mouse_pos: tuple[int, int]) -> None:
        """Détecte la face cliquée et affiche les coordonnées 3D du clic."""
        focal_length: float = HEIGHT * 0.9
        best_hit: tuple[float, int, float, float, float] | None = None

        for index, face in enumerate(FACES):
            pts_2d: list[tuple[int, int]] = []
            for vertex_idx in face:
                proj = self._projected_vertices[vertex_idx]
                if proj is None:
                    break
                pts_2d.append(proj)

            if len(pts_2d) != len(face) or not is_face_visible(pts_2d):
                continue

            if is_point_inside(mouse_pos, pts_2d):
                area: float = polygon_area(pts_2d)
                a = self._rotated_vertices[face[0]]
                b = self._rotated_vertices[face[1]]
                c = self._rotated_vertices[face[-1]]
                hit = intersect_ray_face(
                    mouse_pos,
                    WIDTH,
                    HEIGHT,
                    focal_length,
                    self.camera_distance,
                    a,
                    b,
                    c,
                )
                if hit is not None:
                    x, y, z = hit
                    if best_hit is None or z < best_hit[0]:
                        best_hit = (z, index, area, x, y)

        if best_hit is not None:
            z, index, area, x, y = best_hit
            info: str = (
                f"{SCENE.name} | Face #{index} | "
                f"Aire: {area:.0f} px² | "
                f"Point 3D: x={x:.2f}, y={y:.2f}, z={z:.2f}"
            )
            pg.display.set_caption(info)
            print(info)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            return False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        return True

    def update(
        self, delta_time: float, keys: pg.key.ScancodeWrapper
    ) -> list[tuple[int, int] | None]:
        turn_speed: float = 1.5 * delta_time
        self.angles[0] += (keys[pg.K_z] - keys[pg.K_s]) * turn_speed
        self.angles[1] += (keys[pg.K_q] - keys[pg.K_d]) * turn_speed
        self.angles[2] += (keys[pg.K_a] - keys[pg.K_e]) * turn_speed

        rotation: Matrix = (
            Matrix.rotation_z(self.angles[2])
            @ Matrix.rotation_y(self.angles[1])
            @ Matrix.rotation_x(self.angles[0])
        )
        zoom_speed: float = 3.0 * delta_time
        self.camera_distance += (
            keys[pg.K_DOWN] - keys[pg.K_UP]
        ) * zoom_speed
        self.camera_distance = min(20.0, max(1, self.camera_distance))

        self._rotated_vertices = []
        self._projected_vertices = []
        for x, y, z in VERTICES:
            rotated: Matrix = rotation @ Matrix([[x], [y], [z]])
            self._rotated_vertices.append(
                (rotated[0][0], rotated[1][0], rotated[2][0])
            )
            self._projected_vertices.append(self._project(rotated))
        return self._projected_vertices

    def run(self) -> int:
        return Window().run(self, EDGES)
