# ==============================================================================
# tp - Outils Mathématiques Fondamentaux
# August CONCHIN
#
# tp1 - Calcul numérique
# ==============================================================================

from typing import Callable

import math
import sys

from fractions import Fraction


class tp1:
    def __init__(self) -> None:
        self.exercices: dict[str, Callable] = {
            "1.1": self.exercice1_1,
            "1.2": self.exercice1_2,
            "2.1": self.exercice2_1,
            "2.2": self.exercice2_2,
            "3.1": self.exercice3_1,
            "3.2": self.exercice3_2,
            "4": self.exercice4,
            "5": self.exercice5,
            "6.1": self.exercice6_1,
            "6.2": self.exercice6_2,
            "7.1": self.exercice7_1,
            "7.2": self.exercice7_2,
            "7.3": self.exercice7_3,
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

    def exercice1_1(self) -> int:
        x: int = 2026
        y: int = 7
        quotient: int = x // y
        reste: int = x % y

        print(quotient, reste)
        print(quotient * y + reste == x)
        return 0

    def exercice1_2(self) -> int:
        n: int = 123456789

        print(n % 10)
        print(n // 10)
        return 0

    def exercice2_1(self) -> int:
        total: float = 0.0

        for i in range(1000):
            total += 0.1
        print(total)
        print(total - 100)
        return 0

    def exercice2_2(self) -> int:
        print(presque_egaux(0.1 + 0.2, 0.3))
        print(presque_egaux(1.0, 1.5))
        return 0

    def exercice3_1(self) -> int:
        x: int = 7

        for i in range(1, 11):
            print(f"x x {i} = {x * i}")
        return 0

    def exercice3_2(self) -> int:
        n: int = 100
        total: int = 0

        for i in range(1, n + 1):
            total += i
        print(total)
        print(n * (n + 1) // 2)
        return 0

    def exercice4(self) -> int:
        print(nombre_de_chiffres(2026))
        print(nombre_de_chiffres(7))
        print(nombre_de_chiffres(10**60))
        return 0

    def exercice5(self) -> int:
        print(heron(2))
        print(math.sqrt(2))
        print(abs(heron(2) - math.sqrt(2)) < 1e-12)
        return 0

    def exercice6_1(self) -> int:
        print(vers_binaire(37), vers_binaire(0), vers_binaire(1024))
        print(all(vers_binaire(n) == bin(n)[2:] for n in range(2000)))
        return 0

    def exercice6_2(self) -> int:
        eps: float = 1.0

        while (1.0 + eps / 2 != 1.0):
            eps /= 2
        print(eps)
        print(sys.float_info.epsilon)
        print(eps == 2 ** -52)
        return 0

    def exercice7_1(self) -> int:
        petite: float
        grande: float

        petite, grande = racines_naif(1.0, -1e8, 1.0)
        print(petite, grande)
        print("produit :", petite * grande, "attendu : 1")
        return 0

    def exercice7_2(self) -> int:
        residu: float
        petite: float
        grande: float

        petite, grande = racines(1.0, -1e8, 1.0)
        print(petite, grande)
        print("produit :", petite * grande)
        for x in (petite, grande):
            residu = x * x - 1e8 * x + 1
        print(
            f"residu : {residu:.1e},"
            f"soit {residu / max(x * x, 1.0):.1e} en relatif"
        )
        return 0

    def exercice7_3(self) -> int:
        total: Fraction = Fraction(0)

        for _ in range(1000):
            total += Fraction(1, 10)
        print(total, total == 100)
        print(Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10))
        return 0


def presque_egaux(a, b, tolerance=1e-9):
    return abs(a - b) <= tolerance


def nombre_de_chiffres(n):
    compte: int = 1

    while (n >= 10):
        n //= 10
        compte += 1
    return compte


def heron(a: int, tolerance: float = 1e-12) -> float:
    if a < 0:
        raise ValueError(
            "pas de racine carrée réelle pour un nombre négatif"
        )
    if a == 0:
        return 0.0
    x: float = float(a)
    tours: int = 0
    while True:
        suivant: float = 0.5 * (x + a / x)
        tours += 1
        if abs(suivant - x <= tolerance * abs(suivant)):
            return suivant
        x = suivant


def vers_binaire(n: int) -> str:
    if n == 0:
        return "0"
    chiffres: str = ""
    while (n > 0):
        chiffres = str(n % 2) + chiffres
        n //= 2
    return chiffres


def racines_naif(a: float, b: float, c: float) -> tuple[float, float]:
    delta: float = b * b - 4 * a * c
    if delta < 0:
        raise ValueError("pas de racine réelle")
    r = math.sqrt(delta)
    return (-b - r) / (2 * a), (-b + r) / (2 * a)


def racines(a: float, b: float, c: float) -> tuple[float, float]:
    delta: float = b * b - 4 * a * c
    if delta < 0:
        raise ValueError("pas de racine réelle")
    r = math.sqrt(delta)
    if b >= 0:
        sure: float = (-b - r) / (2 * a)
    else:
        sure: float = (-b + r) / (2 * a)
    autre: float = c / (a * sure)
    return min(sure, autre), max(sure, autre)


if __name__ == "__main__":
    tp1().run()
