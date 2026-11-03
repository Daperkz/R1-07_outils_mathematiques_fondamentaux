# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
#
# window
# ==============================================================================

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from .app import App


WIDTH, HEIGHT = 800, 600
BACKGROUND = (18, 20, 28)
FOREGROUND = (220, 230, 255)


class Window:
    def run(self, app: App, edges: tuple[tuple[int, int], ...]) -> int:
        pg.init()
        screen: pg.Surface = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Custom matrix - wireframe cube")
        clock: pg.time.Clock = pg.time.Clock()
        running: bool = True

        while running:
            delta_time: float = min(clock.tick(60) / 1000, 0.05)

            for event in pg.event.get():
                if not app.handle_event(event):
                    running = False

            projected = app.update(delta_time, pg.key.get_pressed())
            screen.fill(BACKGROUND)
            for start, end in edges:
                first, second = projected[start], projected[end]
                if first is not None and second is not None:
                    pg.draw.line(screen, FOREGROUND, first, second, 2)

            pg.display.flip()

        pg.quit()
        return 0
