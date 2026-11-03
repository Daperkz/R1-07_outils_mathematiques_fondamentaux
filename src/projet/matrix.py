# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# matrix
# ==============================================================================

from __future__ import annotations

from math import cos, sin


class Matrix:
    """Représente une matrice non vide de nombres flottants."""

    def __init__(self, data: list[list[float]]) -> None:
        """Construit une matrice à partir de lignes de valeurs.

        Les valeurs sont stockées en nombres flottants et de façon
        immuable.

        Args:
            data: Lignes non vides de même longueur.

        Raises:
            ValueError: Si la matrice est vide ou si ses lignes n'ont pas la
                même longueur.
        """
        if not data or not data[0]:
            raise ValueError("a matrix must contain at least one value")

        column_count = len(data[0])
        if any(len(row) != column_count for row in data):
            raise ValueError("all matrix rows must have the same length")

        self._data: tuple[tuple[float, ...], ...] = tuple(
            tuple(float(value) for value in row) for row in data
        )
        self.rows: int = len(self._data)
        self.columns: int = column_count

    def __str__(self) -> str:
        """Renvoie une représentation textuelle des valeurs de la matrice."""
        return f"{self._data}"

    def __getitem__(self, row: int) -> tuple[float, ...]:
        """Renvoie la ligne située à l'indice donné."""
        return self._data[row]

    def __eq__(self, other: object) -> bool:
        """Indique si l'autre objet est une matrice de mêmes valeurs."""
        return isinstance(other, Matrix) and self._data == other._data

    def __matmul__(self, other: Matrix) -> Matrix:
        """Multiplie cette matrice par une autre.

        Args:
            other: Matrice à multiplier à droite.

        Returns:
            La matrice produit.

        Raises:
            ValueError: Si le nombre de colonnes de cette matrice diffère du
                nombre de lignes de l'autre.
        """
        if self.columns != other.rows:
            raise ValueError(
                f"cannot multiply shapes {(self.rows, self.columns)} "
                f"and {(other.rows, other.columns)}"
            )

        return Matrix([
            [
                sum(self[row][index] * other[index][column]
                    for index in range(self.columns))
                for column in range(other.columns)
            ]
            for row in range(self.rows)
        ])

    @classmethod
    def rotation_x(cls, angle: float) -> Matrix:
        """Construit la matrice de rotation autour de l'axe X.

        Args:
            angle: Angle de rotation en radians.

        Returns:
            La matrice de rotation 3 × 3.
        """
        c, s = cos(angle), sin(angle)
        return cls([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c],
        ])

    @classmethod
    def rotation_y(cls, angle: float) -> Matrix:
        """Construit la matrice de rotation autour de l'axe Y.

        Args:
            angle: Angle de rotation en radians.

        Returns:
            La matrice de rotation 3 × 3.
        """
        c, s = cos(angle), sin(angle)
        return cls([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c],
        ])

    @classmethod
    def rotation_z(cls, angle: float) -> Matrix:
        """Construit la matrice de rotation autour de l'axe Z.

        Args:
            angle: Angle de rotation en radians.

        Returns:
            La matrice de rotation 3 x 3.
        """
        c, s = cos(angle), sin(angle)
        return cls([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1],
        ])

    @property
    def T(self) -> Matrix:
        """Renvoie la transposée de cette matrice."""
        return self._transpose()

    def _transpose(self) -> Matrix:
        """Construit la transposée de cette matrice."""
        return Matrix([
                [self._data[row][col] for row in range(self.rows)]
                for col in range(self.columns)
        ])
