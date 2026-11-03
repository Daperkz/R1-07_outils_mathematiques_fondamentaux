<!--
================================================================================
Outils Mathématiques Fondamentaux

README
================================================================================
-->
# R1-07_outils_mathematiques_fondamentaux

Projet réalisé par :
- **August CONCHIN**
- **Louay BEN AHMED**
- **Sami BEN SLIMA**

---

## Organisation du dépôt

- `src/tp/` : nos exercices faits pendant les séances de TP (`tp1.py` à `tp4.py`).
- `src/projet/` : le code Python du projet.
- `scenes/` : les fichiers `.txt` qui décrivent les formes 3D (`cube.txt`, `pyramid.txt`, `diamond.txt`, `house.txt`).

---

## Présentation du projet

Le but du projet est d'afficher des formes 3D dans une fenêtre Pygame, de les faire tourner avec des matrices faites à la main (sans `numpy`), et d'interagir avec leurs faces à la souris en utilisant les formules vues en cours et en TP.

### Ce qui a été mis en place (partie interpréteur et géométrie)

1. **Interpréteur de fichiers `.txt` (`parser.py` et dossier `scenes/`)** :
   Au lieu d'écrire les coordonnées des objets en dur dans le code, le programme lit un fichier `.txt` ligne par ligne pour récupérer :
   - les sommets 3D (`VERTEX x y z`),
   - les traits à relier (`EDGE i j`),
   - les faces de l'objet (`FACE i j k ...`),
   - et des transformations de départ (`SCALE`, `ROTATE_X`, `ROTATE_Y`, `ROTATE_Z`, `TRANSLATE`) calculées avec notre classe `Matrix`.

2. **Calculs sur les faces lors d'un clic souris (`geometry.py`)** :
   Quand on clique sur l'objet 3D dans la fenêtre, on utilise plusieurs outils mathématiques du module :
   - **Déterminant 2D (`determinant_2d` et `is_face_visible`)** : calcule le déterminant 2x2 des sommets projetés pour savoir si la face est tournée vers nous ou si elle est cachée à l'arrière.
   - **Lancer de rayon (`is_point_inside`)** : trace une demi-droite horizontale depuis le clic souris et compte combien de côtés de la face elle coupe (impair = on a bien cliqué dans la face).
   - **Formule du lacet (`polygon_area`)** : calcule l'aire exacte de la face à l'écran en pixels.
   - **Pivot de Gauss avec pivot partiel (`solve_gauss` et `intersect_ray_face`)** : comme l'écran est en 2D, on a perdu la profondeur. On résout donc un système de 3 équations à 3 inconnues `(x, y, z)` (les 2 équations de la droite du clic souris et l'équation du plan de la face) pour retrouver directement les coordonnées 3D `(x, y, z)` de l'endroit cliqué sur la face.

3. **Transformations matricielles et affichage** :
   La classe `Matrix` représente les matrices et permet de les multiplier, de les transposer et de construire les matrices de rotation autour des axes X, Y et Z. Ces opérations, réalisées sans `numpy`, servent à transformer les sommets des objets.

   La classe `App` gère les rotations commandées au clavier, la distance de la caméra et la projection en perspective des points 3D sur l'écran. Elle transmet également les clics souris aux calculs géométriques. La classe `Window` crée la fenêtre Pygame, gère la boucle d'affichage et dessine les arêtes.

- **[À compléter par Sami]** : *(explication du menu / choix des figures dans l'interface graphique)*

---

## Comment lancer le projet

Mettre en place une venv:
```bash
python3 -m venv .venv
source ./.venv/bin/activate
```
Installer les dépendances :
```bash
pip install -r requirements.txt
```

Lancer le programme depuis la racine du projet :
```bash
python -m src.projet
```

### Commandes
- `Z` / `S` : tourner sur l'axe X
- `Q` / `D` : tourner sur l'axe Y
- `A` / `E` : tourner sur l'axe Z
- `Flèche Haut` / `Flèche Bas` : zoomer / dézoomer
- `Clic gauche` sur une face : affiche dans le titre de la fenêtre (et dans le terminal) la face touchée, son aire en pixels et les coordonnées 3D `(x, y, z)` du point cliqué trouvées par le pivot de Gauss.
- `[À compléter par Sami pour les contrôles du choix de figure]`
- `Échap` : quitter

---

## Observations et regard critique (partie interpréteur & géométrie)

- **Vérification des calculs au démarrage :**
  Dans `cube.txt`, les sommets du cube vont de `-1` à `1` et la face avant se trouve en `z = -1`. Au démarrage (sans tourner le cube), si on clique pile au milieu de la face avant, le pivot de Gauss renvoie bien `x = 0.00, y = 0.00, z = -1.00`, et si on clique près du coin en haut à droite de la face, on approche de `x = 1.00, y = 1.00, z = -1.00`. L'aire affichée est de `129600 px²` (car la face fait 360x360 pixels à l'écran), et elle diminue quand on recule ou qu'on incline le cube.

- **Problème rencontré et corrigé (l'axe Y de Pygame) :**
  Lors des premiers tests, quand on cliquait sur la face devant nous, le programme sélectionnait la face de derrière à travers le cube. En cherchant l'erreur, on a compris que dans Pygame le point `(0, 0)` est en haut à gauche et l'axe Y descend vers le bas (alors qu'en maths l'axe Y monte vers le haut). Ça inversait le signe du déterminant 2D et faisait croire au programme que les faces de devant étaient de dos. On a corrigé la condition de signe dans `is_face_visible` et on a aussi comparé la coordonnée `z` trouvée par le pivot de Gauss pour toujours retenir la face la plus proche de la caméra.

- **Limites :**
  Pour que le pivot de Gauss donne un résultat juste sur toute une face, il faut que les sommets de cette face dans le fichier `.txt` soient bien sur le même plan (coplanaires) et rangés dans le bon ordre.

---

## Répartition du travail

- **Louay BEN AHMED** : interpréteur de fichiers `.txt` (`parser.py`), création des formes 3D dans `scenes/` (`cube.txt`, `pyramid.txt`, `diamond.txt`, `house.txt`), et calculs géométriques / pivot de Gauss au clic souris (`geometry.py`).
- **August CONCHIN** : fourniture de mes exercices réalisés en TP (`tp1.py` à `tp4.py`), création de la classe `Matrix` et mise en place de la base du projet avec les classes `App` et `Window`.
- **Sami BEN SLIMA** : **[À compléter par Sami]**

### Utilisation de l'IA
On a utilisé l'IA uniquement pour avoir un avis sur notre première idée de projet par rapport aux attendus du sujet, car notre version de base (juste un cube qui tourne) était trop superficielle. Ça nous a permis de trouver des pistes pour mieux réutiliser nos fonctions de TP (ajouter le clic sur les faces avec la géométrie 2D et notre pivot de Gauss), que nous avons ensuite codées et adaptées nous-mêmes à notre projet.
