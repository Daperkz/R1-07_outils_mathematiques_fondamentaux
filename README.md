<!--
================================================================================
Projet - Outils Mathématiques Fondamentaux
August CONCHIN
Louay BEN AHMED
Sami BEN SLIMA

README
================================================================================
-->
# R1-07_outils_mathematiques_fondamentaux

Projet réalisé par :
- **August CONCHIN (Daperkz)**
- **Louay BEN AHMED**
- **Sami BEN SLIMA (sami9z)**

---

## Organisation du dépôt

- `src/tp/` : nos exercices faits pendant les séances de TP (`tp1.py` à `tp4.py`).
- `src/projet/` : le code Python du projet :
  - `__main__.py` : point d'entrée de l'application (`python -m src.projet`).
  - `app.py` : logique principale, rotations, projection 3D -> 2D, gestion des événements et interface graphique interactive.
  - `window.py` : création de la fenêtre Pygame (`800x600`) et boucle d'affichage à 60 FPS.
  - `matrix.py` : classe `Matrix` codée à la main (multiplication, transposée, rotations 3D).
  - `parser.py` : interpréteur de fichiers `.txt` pour charger les scènes 3D (`Scene`, `load_scene`).
  - `geometry.py` : outils géométriques et algébriques (distance point-segment, déterminant 2D, visibilité d'une face, lancer de rayon, formule du lacet, pivot de Gauss et intersection rayon-face).
  - `mesh.py` : manipulation dynamique du maillage 3D pour ajouter ou retirer des cubes sur les faces (`AddedCube`, `add_cube_on_face`, `remove_cube_at_face`).
- `scenes/` : les fichiers `.txt` qui décrivent les formes 3D (`cube.txt`, `pyramid.txt`, `diamond.txt`, `house.txt`).

---

## Présentation du projet

Le but du projet est d'afficher des formes 3D en fil de fer dans une fenêtre Pygame, de les faire tourner avec des matrices faites à la main (sans `numpy`), d'inspecter interactivement leurs composants géométriques (cubes, arêtes, sommets) et de construire ou retirer dynamiquement des cubes sur leurs faces en utilisant les formules vues en cours et en TP.

### Ce qui a été mis en place

1. **Interpréteur de fichiers `.txt` (`parser.py` et dossier `scenes/`)** :
   Au lieu d'écrire les coordonnées des objets en dur dans le code, le programme lit un fichier `.txt` ligne par ligne (par défaut `scenes/cube.txt`) pour récupérer :
   - le nom de l'objet (`NAME ...`),
   - les sommets 3D (`VERTEX x y z`),
   - les traits à relier (`EDGE i j`),
   - les faces de l'objet (`FACE i j k ...`),
   - et des transformations de départ (`SCALE`, `ROTATE_X`, `ROTATE_Y`, `ROTATE_Z`, `TRANSLATE`) calculées avec notre classe `Matrix`.

2. **Outils géométriques et algébriques (`geometry.py`)** :
   Plusieurs fonctions mathématiques ont été codées pour interagir à la souris avec la scène 3D projetée à l'écran :
   - **Distance point-segment (`distance_to_segment`)** : projette orthogonalement la position 2D de la souris sur chaque segment `[AB]` (avec produit scalaire borné entre `0` et `1`) afin de détecter précisément le survol et le clic sur une arête.
   - **Déterminant 2D (`determinant_2d` et `is_face_visible`)** : calcule le déterminant 2x2 des sommets projetés pour savoir si une face est tournée vers la caméra ou cachée à l'arrière.
   - **Lancer de rayon 2D (`is_point_inside`)** : trace une demi-droite horizontale depuis le curseur souris et compte combien de côtés du polygone projeté elle coupe (impair = le curseur est bien à l'intérieur de la face).
   - **Formule du lacet (`polygon_area`)** : calcule l'aire exacte d'une face projetée à l'écran en pixels carrés.
   - **Pivot de Gauss avec pivot partiel (`solve_gauss` et `intersect_ray_face`)** : résout un système de 3 équations à 3 inconnues `(x, y, z)` (les 2 équations du rayon issu du clic souris et l'équation du plan de la face obtenue par produit vectoriel) pour retrouver les coordonnées 3D exactes d'un point cliqué sur une face.

3. **Transformations matricielles et affichage (`matrix.py`, `window.py`, `app.py`)** :
   La classe `Matrix` représente les matrices de flottants et permet de les multiplier (`@`), de les transposer (`.T`) et de construire les matrices de rotation 3x3 autour des axes X, Y et Z sans `numpy`.

   La classe `App` applique ces rotations aux sommets, gère la distance de la caméra et réalise la projection en perspective des points 3D sur l'écran 2D. La classe `Window` initialise Pygame, cadence la boucle d'événements et délègue le dessin complet à `App.draw`.

4. **Interface graphique interactive et édition dynamique de maillage (`app.py` et `mesh.py`)** :
   - **4 modes de sélection en haut à gauche (`Tout`, `Cube`, `Arête`, `Point`)** :
     - Tant qu'aucun bouton n'est activé, un clic dans la scène ne sélectionne rien afin d'éviter les sélections involontaires.
     - **`Tout`** : met en surbrillance jaune l'ensemble de la structure (tous les cubes).
     - **`Cube`** : permet de survoler et de sélectionner un cube individuel (cube de base `#0` ou cubes ajoutés `#1`, `#2`, ...).
     - **`Arête`** : permet de survoler et de cliquer sur une arête pour afficher ses deux sommets 3D et sa longueur euclidienne 3D.
     - **`Point`** : permet de survoler et de cliquer sur un sommet pour afficher ses coordonnées 3D (tournées et au repos), sa projection 2D et la liste des arêtes connectées.
   - **Ajout et retrait dynamique de cubes en haut à droite (`+ Cube` et `- Cube`)** :
     - Lorsque l'un de ces deux boutons est activé, le survol d'une face visible l'illumine légèrement en jaune semi-transparent.
     - **`add_cube_on_face` (`mesh.py`)** : calcule la longueur d'arête de la face ciblée, détermine son vecteur normal unitaire par produit vectoriel, vérifie son orientation vers l'extérieur via un produit scalaire avec le centre de la forme, puis extrude 4 nouveaux sommets, 8 arêtes et 5 nouvelles faces externes.
     - **`remove_cube_at_face` (`mesh.py`)** : retire le cube visé (ainsi que les éventuels cubes greffés par-dessus pour préserver la cohérence des indices) et restaure la face de base initiale, tout en interdisant de supprimer le dernier cube principal.
   - **Bandeau d'informations centré en bas de la fenêtre** :
     - Affiche en permanence sur deux lignes d'une part le résumé global de la scène (nom de l'objet, nombre de cubes, total de sommets, arêtes, faces et distance caméra) et d'autre part les mesures détaillées de l'élément sélectionné ou le guidage du mode actif.

---

## Comment lancer le projet

Mettre en place un environnement virtuel (`venv`) :

- **Sous Linux / macOS** :
```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

- **Sous Windows (PowerShell)** :
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :
```bash
pip install -r requirements.txt
```

Lancer le programme depuis la racine du projet :
```bash
python -m src.projet
```
*(ou `py -m src.projet` sous Windows)*

### Commandes

**Au clavier :**
- `Z` / `S` : tourner sur l'axe X
- `Q` / `D` : tourner sur l'axe Y
- `A` / `E` : tourner sur l'axe Z
- `Flèche Haut` / `Flèche Bas` : zoomer / dézoomer (distance caméra bornée entre `1.0` et `20.0`)
- `Échap` : quitter l'application

**À la souris (interface graphique) :**
- Boutons **`Tout`**, **`Cube`**, **`Arête`**, **`Point`** (en haut à gauche) : activer ou désactiver un mode de sélection, puis faire un `Clic gauche` sur l'élément souhaité dans la scène 3D pour inspecter ses coordonnées et propriétés dans le bandeau inférieur.
- Bouton **`+ Cube`** (en haut à droite) : activer le mode d'ajout, survoler une face (qui s'éclaire en jaune) puis faire un `Clic gauche` pour y greffer un cube de taille adaptée.
- Bouton **`- Cube`** (en haut à droite) : activer le mode de retrait, survoler une face en jaune puis faire un `Clic gauche` pour supprimer le cube correspondant (le cube initial ne peut pas être retiré).

---

## Observations et regard critique

- **Vérification des calculs géométriques au démarrage :**
  Dans `cube.txt`, les sommets du cube vont de `-1` à `1` (arête de longueur `2.00`) et la face avant se trouve en `z = -1`. Lors de la validation des fonctions de `geometry.py` (`intersect_ray_face` et `polygon_area`) au démarrage sans rotation, un clic pile au milieu de la face avant renvoie bien `x = 0.00, y = 0.00, z = -1.00`, et un clic près du coin supérieur droit tend vers `x = 1.00, y = 1.00, z = -1.00`. L'aire projetée vaut `129600 px²` (car la face mesure `360x360` pixels à distance `4.0`) et diminue lorsqu'on recule ou qu'on incline le cube. De même, le mode `Arête` vérifie bien une longueur 3D constante de `2.00` quelle que soit la rotation appliquée, ce qui confirme que nos matrices de rotation sont bien orthogonales (isométries conservant les longueurs).

- **Problèmes rencontrés et corrigés :**
  - **L'axe Y inversé de Pygame :** Lors des premiers tests de sélection de face, cliquer sur la face avant sélectionnait la face arrière à travers le cube. Dans Pygame, l'origine `(0, 0)` est en haut à gauche et l'axe Y descend vers le bas (contrairement au repère mathématique classique), ce qui inversait le signe du déterminant 2D. Nous avons corrigé la condition de signe dans `is_face_visible` et trié les faces candidates selon leur profondeur `z` pour toujours retenir la face visible la plus proche de la caméra.
  - **Affichage des polices système dans Pygame :** Certains caractères spéciaux Unicode (comme les flèches) s'affichaient sous forme de carrés vides selon l'OS ; nous les avons remplacés par des séparateurs standards ASCII/UTF-8 compatibles partout.

- **Limites actuelles :**
  - Pour que les calculs sur une face (visibilité, extrusion ou pivot de Gauss) restent exacts, les sommets d'une même face dans le fichier `.txt` doivent être coplanaires et déclarés dans un ordre cohérent (sens trigonométrique vu de l'extérieur).
  - Lorsqu'on retire un cube ajouté sur lequel d'autres cubes ont été construits, `remove_cube_at_face` retire également les cubes ajoutés après lui afin de conserver une indexation contiguë des sommets.
  - La scène chargée par défaut est `scenes/cube.txt` (pensée pour l'assemblage de cubes), même si l'interpréteur `load_scene` prend déjà en charge les autres scènes du dossier `scenes/` (`pyramid.txt`, `diamond.txt`, `house.txt`) en modifiant le chemin dans `app.py`.

---

## Répartition du travail

- **Louay BEN AHMED** : interpréteur de fichiers `.txt` (`parser.py`), création des formes 3D dans `scenes/` (`cube.txt`, `pyramid.txt`, `diamond.txt`, `house.txt`), et calculs géométriques / pivot de Gauss (`geometry.py`).
- **August CONCHIN (Daperkz)** : fourniture des exercices réalisés en TP (`tp1.py` à `tp4.py`), création de la classe `Matrix`, mise en place de la base du projet (`App`, `Window`), extraction de la gestion du maillage dans `mesh.py` et harmonisation du style de code.
- **Sami BEN SLIMA (sami9z)** : interface graphique interactive dans `app.py` (boutons de sélection `Tout`, `Cube`, `Arête`, `Point`, surbrillance au survol, bandeau d'informations géométriques en temps réel), fonctionnalités d'ajout et de retrait dynamique de cubes sur les faces (`mesh.py`) et calcul de distance point-segment (`distance_to_segment` dans `geometry.py`).

### Utilisation de l'IA
Nous avons utilisé l'IA pour prendre du recul sur notre première idée de projet par rapport aux attendus du sujet (notre base initiale avec un simple cube tournant étant trop limitée), trouver des pistes permettant de mieux exploiter nos outils mathématiques de TP (sélection géométrique 2D/3D, pivot de Gauss, extrusion par produit vectoriel), et nous assister dans la mise en forme de l'interface interactive Pygame.
