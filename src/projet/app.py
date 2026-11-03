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


WIDTH, HEIGHT = 800, 600
BACKGROUND = (18, 20, 28)
FOREGROUND = (220, 230, 255)

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

    def run(self) -> int:
        pg.init()
        screen: pg.Surface = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Custom matrix - wireframe cube")
        clock: pg.time.Clock = pg.time.Clock()
        running: bool = True

        while running:
            delta_time: float = min(clock.tick(60) / 1000, 0.05)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                elif event.type == pg.MOUSEWHEEL:
                    self.camera_distance: float = min(
                        20.0, max(2.5, self.camera_distance - event.y * 0.3)
                    )

            keys = pg.key.get_pressed()
            turn_speed: float = 1.5 * delta_time
            self.angles[0] += (keys[pg.K_w] - keys[pg.K_s]) * turn_speed
            self.angles[1] += (keys[pg.K_a] - keys[pg.K_d]) * turn_speed
            self.angles[2] += (keys[pg.K_q] - keys[pg.K_e]) * turn_speed

            rotation: Matrix = (
                Matrix.rotation_z(self.angles[2])
                @ Matrix.rotation_y(self.angles[1])
                @ Matrix.rotation_x(self.angles[0])
            )
            projected: list[tuple[int, int] | None] = [
                self._project(rotation @ Matrix([[x], [y], [z]]))
                for x, y, z in VERTICES
            ]

            screen.fill(BACKGROUND)
            for start, end in EDGES:
                first, second = projected[start], projected[end]
                if first is not None and second is not None:
                    pg.draw.line(screen, FOREGROUND, first, second, 2)

            pg.display.flip()
        pg.quit()
        return 0
