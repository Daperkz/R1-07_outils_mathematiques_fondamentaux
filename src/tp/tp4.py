# ==============================================================================
# tp - Outils Mathématiques Fondamentaux
# August CONCHIN
#
# tp4 - Matrices et systèmes linéaires
# ==============================================================================

from __future__ import annotations

from typing import Callable
import random

class tp4:
    def __init__(self) -> None:
        self.exercices: dict[str, Callable] = {
            "1": self.getExercice1,
            "2": self.getExercice2,
            "3": self.getExercice3
        }

    def run(self) -> int:
        while True:
            print("\nChoisissez un exercice (0 pour quitter) :")
            print(" ; ".join(self.exercices))
            choix = input("> ").strip()

            if choix == "0":
                break
            if choix in self.exercices:
                self.exercices[choix]()
            else:
                print("Choix invalide.")
        return 0

    def getExercice1(self) -> None:
        A: Matrix = Matrix([
            [1, 2, 2],
            [1, 3, -2],
            [3, 5, 8]
        ])
        print(Matrix([[1, 2, 3], [4, 5, 6]]).T)

    def getExercice2(self) -> None:
        identite: Matrix = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        A: Matrix = Matrix([[1, 2, 2], [1, 3, -2], [3, 5, 8]])

        print(A * identite == A)
        print(Matrix([[1, 2], [3, 4]]) * Matrix([[0, 1], [1, 0]]))

    def getExercice3(self) -> None:
        a: Matrix = Matrix([[1, 2, 2], [1, 3, -2], [3, 5, 8]])
        b: list = [2, -1, 8]
        x = solve(a, b)
        print([round(v, 10) for v in x])

        verif = [sum(a[i][j] * x[j] for j in range(3)) for i in range(3)]
        print([round(v, 10) for v in verif])
        pass

def matrice_aleatoire(size: int) -> Matrix:
    return Matrix([[random.random() for _ in range(size)] for _ in range(size)])

#import numpy as np
#
#A = np.array(
#    [[1.0, 2.0, 2.0],
#    [1.0, 3.0, -2.0],
#    [3.0, 5.0, 8.0]]
#)
#b = np.array([2.0, -1.0, 8.0])
#
#print(A.shape)
#print(A.T)
#print(A @ A)
#print(A * A)

class Matrix:
    def __init__(self, data: list[list[float]], **kwargs) -> None:
        self.data: list[list[float]] = data
        self.rows: int = len(data)
        self.cols: int = len(data[0]) if data else 0
        self.shape: tuple[int, int] = (self.rows, self.cols)

    @property
    def T(self) -> Matrix:
        return self._transpose()

    def __str__(self) -> str:
        return f"{self.data}"

    def __repr__(self) -> str:
        return (
            f"rows: {self.rows}, cols: {self.cols}, "
            f"shape: {self.shape}, data: {self.data}, transpose: {self.T}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.data == other.data

    def _transpose(self) -> Matrix:
        return Matrix([
                [self.data[row][col] for row in range(self.rows)]
                for col in range(self.cols)
        ])

    def __mul__(self, other: Matrix) -> Matrix:
        if other.rows != self.cols:
            raise ValueError("dimensions incompatibles")
        new: list[list[float]] = [[0] * other.cols for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(other.cols):
                somme = 0
                for k in range(self.cols):
                    somme += self.data[i][k] * other.data[k][j]
                new[i][j] = somme
        return Matrix(new)

    def __len__(self) -> int:
        return self.rows

    def __getitem__(self, i: int) -> list[float]:
        return self.data[i]

    def __setitem__(self, i: int, n: list[float]) -> None:
        assert isinstance(n, list) == True, "new value isn't the same type"
        assert len(n) == self.cols, "new value isn't the same lenght as previous"
        self.data[i] = n

def solve(self, b: list[float], tolerance=1e-14):
    """
        Résout A x = b par le pivot de Gauss avec pivot partiel.
        A est une liste de lignes, b une liste. Ni A ni b ne sont modifiés.
        Un pivot inférieur ou égal à tolerance est considéré comme nul.
    """
    n: int = len(self)
    m: Matrix = Matrix([list(self[i]) + [b[i]] for i in range(n)])

    for k in range(n):
        meilleure = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[meilleure][k]) <= tolerance:
            raise ValueError("systeme singulier ou mal pose")
        m[k], m[meilleure] = m[meilleure], m[k]
        for i in range(k + 1, n):
            facteur = m[i][k] / m[k][k]
            for j in range(k, n + 1):
                m[i][j] = m[i][j] - facteur * m[k][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        somme = m[i][n]
        for j in range(i + 1, n):
            somme = somme - m[i][j] * x[j]
        x[i] = somme / m[i][i]
    return x

if __name__ == "__main__":
    tp4().run()
