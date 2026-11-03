# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
#
# matrix
# ==============================================================================

from __future__ import annotations

from math import cos, sin

class Matrix:
    def __init__(self, data: list[list[float]]) -> None:
        if not data or not data[0]:
            raise ValueError("a matrix must contain at least one value")

        column_count = len(data[0])
        if any(len(row) != column_count for row in data):
            raise ValueError("all matrix rows must have the same length")

        self._data: tuple[tuple[float, ...], ...] = tuple(tuple(float(value) for value in row) for row in data)
        self.rows: int = len(self._data)
        self.columns: int = column_count

    def __str__(self) -> str:
        return f"{self._data}"

    def __getitem__(self, row: int) -> tuple[float, ...]:
        return self._data[row]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Matrix) and self._data == other._data

    def __matmul__(self, other: Matrix) -> Matrix:
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
        c, s = cos(angle), sin(angle)
        return cls([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c],
        ])

    @classmethod
    def rotation_y(cls, angle: float) -> Matrix:
        c, s = cos(angle), sin(angle)
        return cls([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c],
        ])

    @classmethod
    def rotation_z(cls, angle: float) -> Matrix:
        c, s = cos(angle), sin(angle)
        return cls([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1],
        ])

    @property
    def T(self) -> Matrix:
        return self._transpose()

    def _transpose(self) -> Matrix:
        return Matrix([
                [self._data[row][col] for row in range(self.rows)]
                for col in range(self.columns)
        ])
