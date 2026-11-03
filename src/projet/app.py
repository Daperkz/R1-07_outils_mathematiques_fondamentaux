# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
#
# app
# ==============================================================================

from __future__ import annotations

import pygame as pg

from .matrix import Matrix
from .window import HEIGHT, WIDTH, Window


VERTICES = (
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
)
EDGES = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
)


class App:
    def __init__(self) -> None:
        self.angles: list[float] = [0.0, 0.0, 0.0]
        self.camera_distance: float = 4.0

    def _project(self, point: Matrix) -> tuple[int, int] | None:
        depth: float = point[2][0] + self.camera_distance
        if depth <= 0.1:
            return None

        focal_length: float = HEIGHT * 0.9
        x: float = WIDTH / 2 + point[0][0] * focal_length / depth
        y: float = HEIGHT / 2 - point[1][0] * focal_length / depth
        return round(x), round(y)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            return False
        return True

    def update(
        self, delta_time: float, keys: pg.key.ScancodeWrapper
    ) -> list[tuple[int, int] | None]:
        turn_speed: float = 1.5 * delta_time
        self.angles[0] += (keys[pg.K_w] - keys[pg.K_s]) * turn_speed
        self.angles[1] += (keys[pg.K_a] - keys[pg.K_d]) * turn_speed
        self.angles[2] += (keys[pg.K_q] - keys[pg.K_e]) * turn_speed

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
        return [
            self._project(rotation @ Matrix([[x], [y], [z]]))
            for x, y, z in VERTICES
        ]

    def run(self) -> int:
        return Window().run(self, EDGES)
