# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# app
# ==============================================================================

from __future__ import annotations

import sys
from pathlib import Path
import pygame as pg

if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from src.projet.geometry import (
        intersect_ray_face,
        is_face_visible,
        is_point_inside,
        polygon_area,
    )
    from src.projet.matrix import Matrix
    from src.projet.parser import Scene, load_scene
    from src.projet.window import HEIGHT, WIDTH, Window
else:
    from .geometry import (
        intersect_ray_face,
        is_face_visible,
        is_point_inside,
        polygon_area,
    )
    from .matrix import Matrix
    from .parser import Scene, load_scene
    from .window import HEIGHT, WIDTH, Window


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SCENE_FILE = REPO_ROOT / "scenes" / "cube.txt"
SCENE_PATH = DEFAULT_SCENE_FILE if DEFAULT_SCENE_FILE.exists() else Path("scenes/cube.txt")

SCENE: Scene = load_scene(str(SCENE_PATH))


class App:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = list(SCENE.vertices)
        self.edges: list[tuple[int, int]] = list(SCENE.edges)
        self.faces: list[tuple[int, ...]] = list(SCENE.faces)
        self.added_cubes: list[dict] = []

        self.angles: list[float] = [0.0, 0.0, 0.0]
        self.camera_distance: float = 4.0
        self._rotated_vertices: list[tuple[float, float, float]] = list(
            self.vertices
        )
        self._projected_vertices: list[tuple[int, int] | None] = []

        # Modes et états de sélection ("cube", "edge", "point", "all", ou None)
        self.selection_mode: str | None = None
        self.selected_cube_idx: int | None = None
        self.selected_edge: int | None = None
        self.selected_point: int | None = None
        self.selected_face: tuple[int, float, float, float, float] | None = None
        self.hovered_cube: int | None = None
        self.hovered_edge: int | None = None
        self.hovered_point: int | None = None

        # Mode d'ajout et de retrait de cube
        self.add_cube_mode: bool = False
        self.remove_cube_mode: bool = False
        self.hovered_face: tuple[int, list[tuple[int, int]]] | None = None

        # Rectangles des 4 boutons de sélection en haut à gauche
        self.btn_all = pg.Rect(15, 15, 80, 32)
        self.btn_cube = pg.Rect(103, 15, 80, 32)
        self.btn_edge = pg.Rect(191, 15, 80, 32)
        self.btn_point = pg.Rect(279, 15, 80, 32)

        # Rectangles des boutons d'ajout et retrait en haut à droite
        self.btn_add_cube = pg.Rect(WIDTH - 215, 15, 95, 32)
        self.btn_remove_cube = pg.Rect(WIDTH - 110, 15, 95, 32)

        self._font: pg.font.Font | None = None
        self._small_font: pg.font.Font | None = None
        self._info_font: pg.font.Font | None = None

    @staticmethod
    def _dist_to_segment(
        p: tuple[int, int], a: tuple[int, int], b: tuple[int, int]
    ) -> float:
        """Calcule la distance entre un point 2D et un segment de droite [a, b]."""
        px, py = p
        ax, ay = a
        bx, by = b
        dx = bx - ax
        dy = by - ay
        l2 = dx * dx + dy * dy
        if l2 == 0:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
        proj_x = ax + t * dx
        proj_y = ay + t * dy
        return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5

    def _project(self, point: Matrix) -> tuple[int, int] | None:
        depth: float = point[2][0] + self.camera_distance
        if depth <= 0.1:
            return None

        focal_length: float = HEIGHT * 0.9
        x: float = WIDTH / 2 + point[0][0] * focal_length / depth
        y: float = HEIGHT / 2 - point[1][0] * focal_length / depth
        return round(x), round(y)

    def _get_cube_data(
        self, cube_idx: int | None
    ) -> tuple[set[int], set[tuple[int, int]]]:
        """Retourne l'ensemble des sommets et des arêtes appartenant à un cube donné."""
        if cube_idx is None:
            return set(), set()
        if cube_idx == 0:
            verts = set(range(len(SCENE.vertices)))
            edges = set(SCENE.edges) | {(b, a) for a, b in SCENE.edges}
            return verts, edges
        if 1 <= cube_idx <= len(self.added_cubes):
            cube = self.added_cubes[cube_idx - 1]
            i0, i1, i2, i3 = cube["base_face"]
            verts = set(cube["base_face"]) | set(cube["new_verts"])
            base_edges = [(i0, i1), (i1, i2), (i2, i3), (i3, i0)]
            raw_edges = set(cube["added_edges"]) | set(base_edges)
            edges = raw_edges | {(b, a) for a, b in raw_edges}
            return verts, edges
        return set(), set()

    def _get_cube_for_face(self, face: tuple[int, ...]) -> int:
        """Retourne l'indice du cube (0 pour le cube de base, 1+ pour les ajoutés) auquel appartient la face."""
        for idx in range(len(self.added_cubes) - 1, -1, -1):
            if any(v in self.added_cubes[idx]["new_verts"] for v in face):
                return idx + 1
        return 0

    def _find_cube_at_pos(self, mouse_pos: tuple[int, int]) -> int | None:
        """Trouve l'indice du cube sous le curseur de la souris."""
        best_z = float("inf")
        best_face: tuple[int, ...] | None = None
        for face in self.faces:
            pts_2d: list[tuple[int, int]] = []
            for v_idx in face:
                if v_idx < len(self._projected_vertices):
                    proj = self._projected_vertices[v_idx]
                    if proj is None:
                        break
                    pts_2d.append(proj)
                else:
                    break

            if len(pts_2d) != len(face) or not is_face_visible(pts_2d):
                continue

            if is_point_inside(mouse_pos, pts_2d):
                avg_z = sum(
                    self._rotated_vertices[v][2] for v in face
                ) / len(face)
                if avg_z < best_z:
                    best_z = avg_z
                    best_face = face

        if best_face is not None:
            return self._get_cube_for_face(best_face)

        min_dist = float("inf")
        best_edge: tuple[int, int] | None = None
        for s, e in self.edges:
            p1 = self._projected_vertices[s]
            p2 = self._projected_vertices[e]
            if p1 is not None and p2 is not None:
                d = self._dist_to_segment(mouse_pos, p1, p2)
                if d < 12 and d < min_dist:
                    min_dist = d
                    best_edge = (s, e)

        if best_edge is not None:
            for idx in range(len(self.added_cubes) - 1, -1, -1):
                if (
                    best_edge[0] in self.added_cubes[idx]["new_verts"]
                    or best_edge[1] in self.added_cubes[idx]["new_verts"]
                ):
                    return idx + 1
            return 0

        return None

    def add_cube_on_face(self, face_idx: int) -> None:
        """Ajoute un nouveau cube de taille par défaut sur la face spécifiée."""
        if face_idx < 0 or face_idx >= len(self.faces):
            return

        face = self.faces[face_idx]
        if len(face) < 4:
            return

        pts = [self.vertices[i] for i in face]
        p0, p1, p2, p3 = pts[0], pts[1], pts[2], pts[3]

        # Taille de côté par défaut (distance entre les 2 premiers sommets de la face)
        s = (
            (p1[0] - p0[0]) ** 2
            + (p1[1] - p0[1]) ** 2
            + (p1[2] - p0[2]) ** 2
        ) ** 0.5
        if s <= 0.001:
            s = 2.0

        # Normale unitaire
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

        # Assurer l'orientation sortante par rapport au centre de l'objet
        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        cz = sum(v[2] for v in self.vertices) / len(self.vertices)
        fcx = (p0[0] + p1[0] + p2[0] + p3[0]) / 4
        fcy = (p0[1] + p1[1] + p2[1] + p3[1]) / 4
        fcz = (p0[2] + p1[2] + p2[2] + p3[2]) / 4
        dot = n[0] * (fcx - cx) + n[1] * (fcy - cy) + n[2] * (fcz - cz)
        if dot < 0:
            n = (-n[0], -n[1], -n[2])

        # Création des 4 nouveaux sommets extrudés
        base_idx = len(self.vertices)
        new_v = [
            (p0[0] + s * n[0], p0[1] + s * n[1], p0[2] + s * n[2]),
            (p1[0] + s * n[0], p1[1] + s * n[1], p1[2] + s * n[2]),
            (p2[0] + s * n[0], p2[1] + s * n[1], p2[2] + s * n[2]),
            (p3[0] + s * n[0], p3[1] + s * n[1], p3[2] + s * n[2]),
        ]
        self.vertices.extend(new_v)

        i0, i1, i2, i3 = face[0], face[1], face[2], face[3]
        k0, k1, k2, k3 = base_idx, base_idx + 1, base_idx + 2, base_idx + 3

        # Arêtes reliant la face aux nouveaux sommets et arêtes supérieures
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
        self.edges.extend(new_edges)

        # Remplacement de la face par les 5 nouvelles faces du cube
        self.faces.pop(face_idx)
        new_faces = [
            (k0, k1, k2, k3),
            (i0, i1, k1, k0),
            (i1, i2, k2, k1),
            (i2, i3, k3, k2),
            (i3, i0, k0, k3),
        ]
        self.faces.extend(new_faces)

        # Enregistrement du cube ajouté pour permettre son retrait ultérieur
        self.added_cubes.append({
            "base_face": tuple(face),
            "new_verts": set(range(base_idx, base_idx + 4)),
            "added_edges": new_edges,
            "added_faces": new_faces,
        })

        self.hovered_face = None
        self._recompute_projection()
        info = f"Nouveau cube ajouté sur la face #{face_idx} !"
        pg.display.set_caption(info)
        print(info)

    def _recompute_projection(self) -> None:
        """Met à jour les sommets tournés et projetés à l'écran."""
        rotation: Matrix = (
            Matrix.rotation_z(self.angles[2])
            @ Matrix.rotation_y(self.angles[1])
            @ Matrix.rotation_x(self.angles[0])
        )
        self._rotated_vertices = []
        self._projected_vertices = []
        for x, y, z in self.vertices:
            rotated: Matrix = rotation @ Matrix([[x], [y], [z]])
            self._rotated_vertices.append(
                (rotated[0][0], rotated[1][0], rotated[2][0])
            )
            self._projected_vertices.append(self._project(rotated))

    def remove_cube_at_face(self, face_idx: int) -> bool:
        """Retire le cube associé à la face sélectionnée (ou le dernier cube ajouté)."""
        if not self.added_cubes:
            info = "Impossible de retirer le cube principal : au moins 1 cube requis"
            pg.display.set_caption(info)
            print(info)
            return False

        if face_idx < 0 or face_idx >= len(self.faces):
            target_cube_idx = len(self.added_cubes) - 1
        else:
            clicked_face = self.faces[face_idx]
            target_cube_idx = -1
            # Chercher dans quel cube ajouté cette face est présente
            for idx in range(len(self.added_cubes) - 1, -1, -1):
                cube = self.added_cubes[idx]
                if any(v in cube["new_verts"] for v in clicked_face):
                    target_cube_idx = idx
                    break

            if target_cube_idx == -1:
                target_cube_idx = len(self.added_cubes) - 1

        # Retirer tous les cubes dépendants du dernier jusqu'à target_cube_idx
        for _ in range(len(self.added_cubes) - 1, target_cube_idx - 1, -1):
            cube = self.added_cubes.pop()
            # 1. Retirer les 5 faces du cube
            for f in cube["added_faces"]:
                if f in self.faces:
                    self.faces.remove(f)
            # 2. Restaurer la face de base dans l'objet parent
            self.faces.append(cube["base_face"])
            # 3. Retirer les 8 arêtes ajoutées
            for e in cube["added_edges"]:
                if e in self.edges:
                    self.edges.remove(e)
                elif (e[1], e[0]) in self.edges:
                    self.edges.remove((e[1], e[0]))
            # 4. Retirer les 4 sommets
            for _ in range(4):
                if self.vertices:
                    self.vertices.pop()

        self.hovered_face = None
        self.hovered_cube = None
        self.selected_cube_idx = None
        self.selected_edge = None
        self.selected_point = None
        self.selected_face = None
        self._recompute_projection()

        info = f"Cube retiré avec succès ({len(self.vertices)} sommets restants)"
        pg.display.set_caption(info)
        print(info)
        return True

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            return False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Clic sur le bouton "+ Cube" en haut à droite
            if self.btn_add_cube.collidepoint(mouse_pos):
                self.add_cube_mode = not self.add_cube_mode
                self.remove_cube_mode = False
                if self.add_cube_mode:
                    self.selection_mode = None
                    pg.display.set_caption(
                        "Mode AJOUT CUBE actif : survolez une face en jaune puis cliquez dessus"
                    )
                else:
                    pg.display.set_caption("Mode AJOUT CUBE désactivé")
                return True

            # Clic sur le bouton "- Cube" en haut à droite
            if self.btn_remove_cube.collidepoint(mouse_pos):
                self.remove_cube_mode = not self.remove_cube_mode
                self.add_cube_mode = False
                if self.remove_cube_mode:
                    self.selection_mode = None
                    pg.display.set_caption(
                        "Mode RETRAIT CUBE actif : cliquez sur une face en jaune pour retirer le cube"
                    )
                else:
                    pg.display.set_caption("Mode RETRAIT CUBE désactivé")
                return True

            # Clic sur le bouton "Cube" (sélection d'un cube individuel)
            if self.btn_cube.collidepoint(mouse_pos):
                self.add_cube_mode = False
                self.remove_cube_mode = False
                if self.selection_mode == "cube":
                    self.selection_mode = None
                    self.selected_cube_idx = None
                else:
                    self.selection_mode = "cube"
                    self.selected_cube_idx = None
                    self.selected_edge = None
                    self.selected_point = None
                    self.selected_face = None
                    pg.display.set_caption(
                        "Mode CUBE - Cliquez sur un cube pour le sélectionner"
                    )
                return True

            # Clic sur le bouton "Arête"
            if self.btn_edge.collidepoint(mouse_pos):
                self.add_cube_mode = False
                self.remove_cube_mode = False
                if self.selection_mode == "edge":
                    self.selection_mode = None
                    self.selected_edge = None
                else:
                    self.selection_mode = "edge"
                    self.selected_cube_idx = None
                    self.selected_edge = None
                    self.selected_point = None
                    self.selected_face = None
                    pg.display.set_caption(
                        "Mode ARÊTE - Cliquez sur une arête pour la sélectionner"
                    )
                return True

            # Clic sur le bouton "Point"
            if self.btn_point.collidepoint(mouse_pos):
                self.add_cube_mode = False
                self.remove_cube_mode = False
                if self.selection_mode == "point":
                    self.selection_mode = None
                    self.selected_point = None
                else:
                    self.selection_mode = "point"
                    self.selected_cube_idx = None
                    self.selected_edge = None
                    self.selected_point = None
                    self.selected_face = None
                    pg.display.set_caption(
                        "Mode POINT - Cliquez sur un point pour le sélectionner"
                    )
                return True

            # Clic sur le bouton "Tout" (sélectionner tous les cubes)
            if self.btn_all.collidepoint(mouse_pos):
                self.add_cube_mode = False
                self.remove_cube_mode = False
                if self.selection_mode == "all":
                    self.selection_mode = None
                else:
                    self.selection_mode = "all"
                    self.selected_cube_idx = None
                    self.selected_edge = None
                    self.selected_point = None
                    self.selected_face = None
                    pg.display.set_caption(
                        "Mode TOUT - Tous les cubes sont sélectionnés en jaune"
                    )
                return True

            # Clic en mode ajout de cube : greffer le cube sur la face cliquée
            if self.add_cube_mode:
                target_face = None
                if self.hovered_face is not None:
                    target_face = self.hovered_face[0]
                else:
                    best_z = float("inf")
                    for f_idx, face in enumerate(self.faces):
                        pts_2d = []
                        for v_idx in face:
                            if v_idx < len(self._projected_vertices):
                                proj = self._projected_vertices[v_idx]
                                if proj is None:
                                    break
                                pts_2d.append(proj)
                        if (
                            len(pts_2d) == len(face)
                            and is_face_visible(pts_2d)
                            and is_point_inside(mouse_pos, pts_2d)
                        ):
                            avg_z = sum(
                                self._rotated_vertices[v][2] for v in face
                            ) / len(face)
                            if avg_z < best_z:
                                best_z = avg_z
                                target_face = f_idx

                if target_face is not None:
                    self.add_cube_on_face(target_face)
                    return True

            # Clic en mode retrait de cube : supprimer le cube ciblé
            if self.remove_cube_mode:
                target_face = None
                if self.hovered_face is not None:
                    target_face = self.hovered_face[0]
                else:
                    best_z = float("inf")
                    for f_idx, face in enumerate(self.faces):
                        pts_2d = []
                        for v_idx in face:
                            if v_idx < len(self._projected_vertices):
                                proj = self._projected_vertices[v_idx]
                                if proj is None:
                                    break
                                pts_2d.append(proj)
                        if (
                            len(pts_2d) == len(face)
                            and is_face_visible(pts_2d)
                            and is_point_inside(mouse_pos, pts_2d)
                        ):
                            avg_z = sum(
                                self._rotated_vertices[v][2] for v in face
                            ) / len(face)
                            if avg_z < best_z:
                                best_z = avg_z
                                target_face = f_idx

                if target_face is not None:
                    self.remove_cube_at_face(target_face)
                    return True
                elif self.added_cubes:
                    self.remove_cube_at_face(-1)
                    return True

            # Sélection selon le mode actif (uniquement si un bouton est activé)
            if self.selection_mode == "point":
                closest_idx = None
                min_dist = float("inf")
                for idx, pt in enumerate(self._projected_vertices):
                    if pt is not None:
                        d = (
                            (pt[0] - mouse_pos[0]) ** 2
                            + (pt[1] - mouse_pos[1]) ** 2
                        ) ** 0.5
                        if d < min_dist:
                            min_dist = d
                            closest_idx = idx

                if closest_idx is not None and min_dist <= 20:
                    self.selected_point = closest_idx
                    p3d = self._rotated_vertices[closest_idx]
                    info = (
                        f"Point #{closest_idx} sélectionné en jaune | "
                        f"3D: x={p3d[0]:.2f}, y={p3d[1]:.2f}, z={p3d[2]:.2f}"
                    )
                    pg.display.set_caption(info)
                    print(info)
                return True

            if self.selection_mode == "edge":
                closest_edge = None
                min_dist = float("inf")
                for idx, (s, e) in enumerate(self.edges):
                    p1 = self._projected_vertices[s]
                    p2 = self._projected_vertices[e]
                    if p1 is not None and p2 is not None:
                        d = self._dist_to_segment(mouse_pos, p1, p2)
                        if d < min_dist:
                            min_dist = d
                            closest_edge = idx

                if closest_edge is not None and min_dist <= 15:
                    self.selected_edge = closest_edge
                    s, e = self.edges[closest_edge]
                    info = f"Arête #{closest_edge} sélectionnée en jaune (sommets {s}-{e})"
                    pg.display.set_caption(info)
                    print(info)
                return True

            if self.selection_mode == "cube":
                clicked_cube = self._find_cube_at_pos(mouse_pos)
                if clicked_cube is not None:
                    self.selected_cube_idx = clicked_cube
                    info = f"Cube #{clicked_cube} sélectionné en jaune"
                    pg.display.set_caption(info)
                    print(info)
                return True

            # Si aucun mode de sélection n'est actif, le clic ne sélectionne rien

        return True

    def update(
        self, delta_time: float, keys: pg.key.ScancodeWrapper
    ) -> list[tuple[int, int] | None]:
        turn_speed: float = 1.5 * delta_time
        self.angles[0] += (keys[pg.K_z] - keys[pg.K_s]) * turn_speed
        self.angles[1] += (keys[pg.K_q] - keys[pg.K_d]) * turn_speed
        self.angles[2] += (keys[pg.K_a] - keys[pg.K_e]) * turn_speed

        zoom_speed: float = 3.0 * delta_time
        self.camera_distance += (
            keys[pg.K_DOWN] - keys[pg.K_UP]
        ) * zoom_speed
        self.camera_distance = min(20.0, max(1, self.camera_distance))

        self._recompute_projection()

        # Calcul du survol (hover)
        mouse_pos = pg.mouse.get_pos()
        self.hovered_cube = None
        self.hovered_edge = None
        self.hovered_point = None
        self.hovered_face = None

        # 1. Survol d'une face : uniquement lorsque le mode ajout ou retrait de cube est activé
        if self.add_cube_mode or self.remove_cube_mode:
            best_z = float("inf")
            for f_idx, face in enumerate(self.faces):
                pts_2d: list[tuple[int, int]] = []
                for v_idx in face:
                    if v_idx < len(self._projected_vertices):
                        proj = self._projected_vertices[v_idx]
                        if proj is None:
                            break
                        pts_2d.append(proj)
                    else:
                        break

                if len(pts_2d) != len(face) or not is_face_visible(pts_2d):
                    continue

                if is_point_inside(mouse_pos, pts_2d):
                    avg_z = sum(
                        self._rotated_vertices[v][2] for v in face
                    ) / len(face)
                    if avg_z < best_z:
                        best_z = avg_z
                        self.hovered_face = (f_idx, pts_2d)

        # 2. Survol d'un cube en mode cube
        if self.selection_mode == "cube":
            self.hovered_cube = self._find_cube_at_pos(mouse_pos)

        # 3. Survol d'une arête en mode arête
        elif self.selection_mode == "edge":
            min_dist = float("inf")
            for idx, (s, e) in enumerate(self.edges):
                p1 = self._projected_vertices[s]
                p2 = self._projected_vertices[e]
                if p1 is not None and p2 is not None:
                    d = self._dist_to_segment(mouse_pos, p1, p2)
                    if d < 15 and d < min_dist:
                        min_dist = d
                        self.hovered_edge = idx

        # 4. Survol d'un point en mode point
        elif self.selection_mode == "point":
            min_dist = float("inf")
            for idx, pt in enumerate(self._projected_vertices):
                if pt is not None:
                    d = (
                        (pt[0] - mouse_pos[0]) ** 2
                        + (pt[1] - mouse_pos[1]) ** 2
                    ) ** 0.5
                    if d < 20 and d < min_dist:
                        min_dist = d
                        self.hovered_point = idx

        return self._projected_vertices

    def draw(self, screen: pg.Surface) -> None:
        """Dessine les éléments 3D en fonction du mode de sélection et les boutons."""
        YELLOW_SELECTABLE = (220, 200, 70)
        YELLOW_BRIGHT = (255, 255, 0)
        COLOR_DEFAULT = (200, 215, 240)

        # 0. Tracé de la face survolée (uniquement avec le bouton +Cube ou -Cube pressé)
        if (self.add_cube_mode or self.remove_cube_mode) and self.hovered_face is not None:
            _, face_pts = self.hovered_face
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            pg.draw.polygon(overlay, (255, 235, 80, 80), face_pts)
            pg.draw.polygon(overlay, (255, 220, 50, 180), face_pts, 2)
            screen.blit(overlay, (0, 0))

        sel_cube_verts, sel_cube_edges = self._get_cube_data(
            self.selected_cube_idx
        )
        hov_cube_verts, hov_cube_edges = self._get_cube_data(
            self.hovered_cube
        )

        # 1. Tracé des arêtes
        for idx, (start, end) in enumerate(self.edges):
            p1 = self._projected_vertices[start]
            p2 = self._projected_vertices[end]
            if p1 is None or p2 is None:
                continue

            color = COLOR_DEFAULT
            width = 2

            if self.selection_mode == "all":
                color = YELLOW_BRIGHT
                width = 3
            elif self.selection_mode == "cube":
                if (start, end) in sel_cube_edges:
                    color = YELLOW_BRIGHT
                    width = 4
                elif (start, end) in hov_cube_edges:
                    color = YELLOW_BRIGHT
                    width = 3
                else:
                    color = YELLOW_SELECTABLE
                    width = 2
            elif self.selection_mode == "edge":
                if idx == self.selected_edge:
                    color = YELLOW_BRIGHT
                    width = 4
                elif idx == self.hovered_edge:
                    color = YELLOW_BRIGHT
                    width = 3
                else:
                    color = YELLOW_SELECTABLE
                    width = 2

            pg.draw.line(screen, color, p1, p2, width)

        # 2. Tracé des points (sommets)
        for idx, pt in enumerate(self._projected_vertices):
            if pt is None:
                continue

            if self.selection_mode == "all":
                pg.draw.circle(screen, YELLOW_BRIGHT, pt, 5)
            elif self.selection_mode == "cube":
                if idx in sel_cube_verts:
                    pg.draw.circle(screen, YELLOW_BRIGHT, pt, 6)
                elif idx in hov_cube_verts:
                    pg.draw.circle(screen, YELLOW_BRIGHT, pt, 5)
            elif self.selection_mode == "point":
                if idx == self.selected_point:
                    pg.draw.circle(screen, YELLOW_BRIGHT, pt, 8)
                    pg.draw.circle(screen, (255, 255, 255), pt, 12, 2)
                elif idx == self.hovered_point:
                    pg.draw.circle(screen, YELLOW_BRIGHT, pt, 7)
                else:
                    pg.draw.circle(screen, YELLOW_SELECTABLE, pt, 5)

        # 3. Tracé des boutons UI (haut gauche + haut droite)
        self._draw_buttons(screen)

        # 4. Informations détaillées centrées en bas d'écran
        self._draw_bottom_info(screen)

    def _get_general_info_text(self) -> str:
        """Informations globales de l'objet et de la scène (visibles en permanence)."""
        nb_cubes = 1 + len(self.added_cubes)
        return (
            f"Objet : {SCENE.name} ({nb_cubes} cube{'s' if nb_cubes > 1 else ''})   |   "
            f"{len(self.vertices)} sommets   |   "
            f"{len(self.edges)} arêtes   |   "
            f"{len(self.faces)} faces   |   "
            f"Distance caméra : {self.camera_distance:.1f}"
        )

    def _get_selected_info_text(self) -> str:
        """Informations spécifiques à l'élément actuellement sélectionné."""
        if self.add_cube_mode:
            if self.hovered_face is not None:
                f_idx = self.hovered_face[0]
                return f"Mode Ajout Cube : Cliquez sur la face #{f_idx} (en jaune) pour y greffer un cube"
            return "Mode Ajout Cube actif : Survolez une face en jaune puis cliquez dessus"

        if self.remove_cube_mode:
            if self.hovered_face is not None:
                f_idx = self.hovered_face[0]
                return f"Mode Retrait Cube : Cliquez sur la face #{f_idx} (en jaune) pour retirer le cube"
            return "Mode Retrait Cube actif : Survolez une face en jaune puis cliquez pour retirer le cube"

        if self.selection_mode == "all":
            nb_cubes = 1 + len(self.added_cubes)
            return (
                f"Sélection : Tous les cubes ({nb_cubes} cube{'s' if nb_cubes > 1 else ''})   |   "
                f"{len(self.vertices)} sommets   |   "
                f"{len(self.edges)} arêtes   |   "
                f"{len(self.faces)} faces"
            )

        if self.selection_mode == "cube" and self.selected_cube_idx is not None:
            c_idx = self.selected_cube_idx
            c_verts, _ = self._get_cube_data(c_idx)
            if c_verts:
                cx = sum(self._rotated_vertices[v][0] for v in c_verts) / len(c_verts)
                cy = sum(self._rotated_vertices[v][1] for v in c_verts) / len(c_verts)
                cz = sum(self._rotated_vertices[v][2] for v in c_verts) / len(c_verts)
                ox = sum(self.vertices[v][0] for v in c_verts) / len(c_verts)
                oy = sum(self.vertices[v][1] for v in c_verts) / len(c_verts)
                oz = sum(self.vertices[v][2] for v in c_verts) / len(c_verts)
                return (
                    f"Sélection : Cube #{c_idx}   |   "
                    f"Centre 3D tourné : ({cx:+.2f}, {cy:+.2f}, {cz:+.2f})   |   "
                    f"Centre 3D repos : ({ox:+.2f}, {oy:+.2f}, {oz:+.2f})   |   "
                    f"8 sommets, 12 arêtes"
                )

        if self.selection_mode == "point" and self.selected_point is not None:
            idx = self.selected_point
            p3d = self._rotated_vertices[idx]
            orig = self.vertices[idx]
            proj = self._projected_vertices[idx]
            proj_str = (
                f"Écran 2D : ({proj[0]}, {proj[1]})" if proj else "Hors écran"
            )
            connected = [
                f"{s}-{e}"
                for s, e in self.edges
                if s == idx or e == idx
            ]
            conn_str = ", ".join(connected)
            return (
                f"Sélection : Point #{idx}   |   "
                f"3D tourné : ({p3d[0]:+.2f}, {p3d[1]:+.2f}, {p3d[2]:+.2f})   |   "
                f"3D repos : ({orig[0]:+.2f}, {orig[1]:+.2f}, {orig[2]:+.2f})   |   "
                f"{proj_str}   |   Arêtes : [{conn_str}]"
            )

        if self.selection_mode == "edge" and self.selected_edge is not None:
            idx = self.selected_edge
            s, e = self.edges[idx]
            p1 = self.vertices[s]
            p2 = self.vertices[e]
            length = (
                (p2[0] - p1[0]) ** 2
                + (p2[1] - p1[1]) ** 2
                + (p2[2] - p1[2]) ** 2
            ) ** 0.5
            r1 = self._rotated_vertices[s]
            r2 = self._rotated_vertices[e]
            return (
                f"Sélection : Arête #{idx}   |   "
                f"Sommet {s} ({r1[0]:+.2f}, {r1[1]:+.2f}, {r1[2]:+.2f}) ; "
                f"Sommet {e} ({r2[0]:+.2f}, {r2[1]:+.2f}, {r2[2]:+.2f})   |   "
                f"Longueur 3D : {length:.2f}"
            )

        return "Sélection : Aucun élément sélectionné (cliquez sur Cube, Arête, Point ou Tout)"

    def _draw_bottom_info(self, screen: pg.Surface) -> None:
        """Affiche les informations globales et de l'élément sélectionné centrées en bas d'écran."""
        if self._info_font is None:
            self._info_font = pg.font.SysFont(
                "Segoe UI, Arial, sans-serif", 13, bold=True
            )

        general_text = self._get_general_info_text()
        selected_text = self._get_selected_info_text()
        has_selection = (
            self.add_cube_mode
            or self.remove_cube_mode
            or not selected_text.startswith("Sélection : Aucun")
        )

        # Rendu des 2 lignes (globale et sélection)
        surf_general = self._info_font.render(
            general_text, True, (180, 215, 255)
        )
        color_sel = (255, 235, 70) if has_selection else (150, 165, 190)
        surf_selected = self._info_font.render(
            selected_text, True, color_sel
        )

        w = max(surf_general.get_width(), surf_selected.get_width())
        h = surf_general.get_height() + surf_selected.get_height() + 4

        pad_x = 20
        pad_y = 8
        bg_rect = pg.Rect(
            0, 0, w + pad_x * 2, h + pad_y * 2
        )
        bg_rect.centerx = WIDTH // 2
        bg_rect.bottom = HEIGHT - 10

        r_general = surf_general.get_rect(
            centerx=bg_rect.centerx, top=bg_rect.top + pad_y
        )
        r_selected = surf_selected.get_rect(
            centerx=bg_rect.centerx, bottom=bg_rect.bottom - pad_y
        )

        # Cadre avec fond sombre et bordure adaptée
        border_color = (255, 215, 0) if has_selection else (70, 85, 115)
        pg.draw.rect(screen, (16, 20, 30), bg_rect, border_radius=8)
        pg.draw.rect(screen, border_color, bg_rect, width=2, border_radius=8)

        screen.blit(surf_general, r_general)
        screen.blit(surf_selected, r_selected)

    def _draw_buttons(self, screen: pg.Surface) -> None:
        """Affiche les boutons à gauche et les boutons d'ajout/retrait à droite."""
        if self._font is None:
            self._font = pg.font.SysFont("Segoe UI, Arial, sans-serif", 14, bold=True)
            self._small_font = pg.font.SysFont("Segoe UI, Arial, sans-serif", 12)

        mouse_pos = pg.mouse.get_pos()

        # 1. Boutons en haut à gauche
        buttons_left = [
            ("all", "Tout", self.btn_all),
            ("cube", "Cube", self.btn_cube),
            ("edge", "Arête", self.btn_edge),
            ("point", "Point", self.btn_point),
        ]

        for mode_id, label, rect in buttons_left:
            is_active = self.selection_mode == mode_id
            is_hover = rect.collidepoint(mouse_pos)

            if is_active:
                bg_color = (255, 215, 0)
                text_color = (20, 20, 25)
                border_color = (255, 245, 140)
            elif is_hover:
                bg_color = (50, 60, 80)
                text_color = (255, 255, 255)
                border_color = (130, 150, 190)
            else:
                bg_color = (30, 35, 48)
                text_color = (190, 205, 230)
                border_color = (65, 75, 100)

            pg.draw.rect(screen, bg_color, rect, border_radius=6)
            pg.draw.rect(screen, border_color, rect, width=2, border_radius=6)

            text_surf = self._font.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        # 2. Boutons "+ Cube" et "- Cube" en haut à droite
        buttons_right = [
            (self.btn_add_cube, "+ Cube", self.add_cube_mode),
            (self.btn_remove_cube, "- Cube", self.remove_cube_mode),
        ]

        for rect, label, is_active in buttons_right:
            is_hover = rect.collidepoint(mouse_pos)

            if is_active:
                bg_color = (255, 215, 0)
                text_color = (20, 20, 25)
                border_color = (255, 245, 140)
            elif is_hover:
                bg_color = (50, 60, 80)
                text_color = (255, 255, 255)
                border_color = (130, 150, 190)
            else:
                bg_color = (30, 35, 48)
                text_color = (200, 215, 240)
                border_color = (65, 75, 100)

            pg.draw.rect(screen, bg_color, rect, border_radius=6)
            pg.draw.rect(screen, border_color, rect, width=2, border_radius=6)

            surf = self._font.render(label, True, text_color)
            r = surf.get_rect(center=rect.center)
            screen.blit(surf, r)

        # Message de guidage sous les boutons de gauche
        status_msg = ""
        if self.add_cube_mode:
            status_msg = "Mode AJOUT CUBE : cliquez sur une face survolée en jaune"
        elif self.remove_cube_mode:
            status_msg = "Mode RETRAIT CUBE : cliquez sur une face en jaune pour retirer le cube"
        elif self.selection_mode == "all":
            status_msg = "Mode TOUT actif : tous les cubes sont sélectionnés en jaune"
        elif self.selection_mode == "cube":
            if self.selected_cube_idx is not None:
                status_msg = f"Cube #{self.selected_cube_idx} sélectionné"
            else:
                status_msg = "Mode CUBE : survolez/cliquez sur un cube en jaune"
        elif self.selection_mode == "edge":
            if self.selected_edge is not None:
                s, e = self.edges[self.selected_edge]
                status_msg = f"Arête #{self.selected_edge} sélectionnée (sommets {s}-{e})"
            else:
                status_msg = "Mode ARÊTE : survolez/cliquez sur une arête en jaune"
        elif self.selection_mode == "point":
            if self.selected_point is not None:
                p3d = self._rotated_vertices[self.selected_point]
                status_msg = (
                    f"Point #{self.selected_point} sélectionné : "
                    f"({p3d[0]:.2f}, {p3d[1]:.2f}, {p3d[2]:.2f})"
                )
            else:
                status_msg = "Mode POINT : survolez/cliquez sur un sommet en jaune"

        if status_msg and self._small_font is not None:
            msg_surf = self._small_font.render(
                status_msg, True, (255, 240, 150)
            )
            screen.blit(msg_surf, (15, 54))

    def run(self) -> int:
        return Window().run(self, tuple(self.edges))


if __name__ == "__main__":
    App().run()
