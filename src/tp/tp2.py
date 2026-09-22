# ==============================================================================
# Outils Mathématiques Fondamentaux
#
# tp2 - Arithmétique et nombres premiers
# ==============================================================================

from typing import Callable

import time

class tp2:
    def __init__(self) -> None:
        self.exercices: dict[str, Callable] = {
            "1.1": self.exercice1_1,
            "2.1": self.exercice2_1,
            "3.1": self.exercice3_1,
            "4.1": self.exercice4_1,
            "5.1": self.exercice5_1,
            "6.1": self.exercice6_1,
            "6.2": self.exercice6_2,
            "6.3": self.exercice6_3,
            "7.1": self.exercice7_1,
            "7.2": self.exercice7_2,
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

    def exercice1_1(self) -> None:
        print("diviseurs(28):", diviseurs(28))

    def exercice2_1(self) -> None:
        print("pgcd_naif(1071, 462):", pgcd_naif(1071, 462))
        print("pgcd(1071, 462):", pgcd(1071, 462))

    def exercice3_1(self) -> None:
        nombres = [10_007, 100_003, 1_000_003]
        for nombre in nombres:
            temps_naif = duree(est_premier_naif, nombre)
            temps_rapide = duree(est_premier, nombre)
            print(
                nombre,
                f"naif: {temps_naif:.6f} s",
                f"racine: {temps_rapide:.6f} s",
            )

    def exercice4_1(self) -> None:
        premiers = crible(100_000)
        print("premiers sous 100000:", len(premiers))

    def exercice5_1(self) -> None:
        resultat = facteurs(360)
        produit = 1
        for facteur in resultat:
            produit *= facteur
        print("facteurs(360):", resultat)
        print("produit:", produit)

    def exercice5(self) -> None:
        self.exercice5_1()

    def exercice6_1(self) -> None:
        for nombre in [20, 25, 30]:
            print(
                f"fibonacci_recursif({nombre}):",
                f"{duree(fibonacci_recursif, nombre):.6f} s",
            )

    def exercice6_2(self) -> None:
        compteur = {1: 0}

        def fibonacci_compte(n: int) -> int:
            if n == 1:
                compteur[1] += 1
            if n < 2:
                return n
            return fibonacci_compte(n - 1) + fibonacci_compte(n - 2)

        fibonacci_compte(30)
        print("appels de F(1) pour F(30):", compteur[1])

    def exercice6_3(self) -> None:
        nombre_de_chiffres = len(str(fibonacci(10_000)))
        print("nombre de chiffres de fibonacci(10000):", nombre_de_chiffres)

    def exercice7_1(self) -> None:
        resultat = euclide_etendu(1071, 462)
        print("euclide_etendu(1071, 462):", resultat)
        print(1071 * resultat[1] + 462 * resultat[2])

    def exercice7_2(self) -> None:
        arguments = (7, 107, 1_000_003)
        naive = puissance_mod_naive(*arguments)
        rapide = puissance_mod(*arguments)
        print("puissance mod naïve:", naive)
        print("puissance mod rapide:", rapide)
        print("pow Python:", pow(*arguments))


def diviseurs(n: int) -> list[int]:
    """Renvoie les diviseurs positifs de n dans l'ordre croissant."""
    if n <= 0:
        raise ValueError("n doit être un entier strictement positif")

    resultat: list[int] = []
    for diviseur in range(1, n + 1):
        if n % diviseur == 0:
            resultat.append(diviseur)
    return resultat


def pgcd_naif(a: int, b: int) -> int:
    """Calcule le PGCD en essayant tous les diviseurs possibles."""
    a, b = abs(a), abs(b)
    resultat = 0
    for diviseur in range(1, min(a, b) + 1):
        if a % diviseur == 0 and b % diviseur == 0:
            resultat = diviseur
    return resultat


def pgcd(a: int, b: int) -> int:
    """Calcule le PGCD avec l'algorithme d'Euclide."""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def est_premier_naif(n: int) -> bool:
    """Teste la primalité en essayant tous les diviseurs jusqu'à n - 1."""
    if n < 2:
        return False
    for diviseur in range(2, n):
        if n % diviseur == 0:
            return False
    return True


def est_premier(n: int) -> bool:
    """Teste la primalité en s'arrêtant à la racine carrée de n."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2

    diviseur = 3
    while diviseur * diviseur <= n:
        if n % diviseur == 0:
            return False
        diviseur += 2
    return True


def duree(fonction, argument: int) -> float:
    """Renvoie la durée d'exécution de fonction(argument), en secondes."""
    debut = time.perf_counter()
    fonction(argument)
    return time.perf_counter() - debut


def crible(limite: int) -> list[int]:
    """Renvoie la liste des nombres premiers de 2 à limite inclus."""
    if limite < 0:
        raise ValueError("limite doit être positive ou nulle")

    est_premier_tab = [True] * (limite + 1)
    if limite >= 0:
        est_premier_tab[0] = False
    if limite >= 1:
        est_premier_tab[1] = False

    diviseur = 2
    while diviseur * diviseur <= limite:
        if est_premier_tab[diviseur]:
            for multiple in range(diviseur * diviseur, limite + 1, diviseur):
                est_premier_tab[multiple] = False
        diviseur += 1

    return [n for n in range(limite + 1) if est_premier_tab[n]]


def facteurs(n: int) -> list[int]:
    """Renvoie les facteurs premiers de n, avec leurs répétitions."""
    if n < 2:
        raise ValueError("n doit être supérieur ou égal à 2")

    resultat: list[int] = []
    diviseur = 2
    while diviseur * diviseur <= n:
        while n % diviseur == 0:
            resultat.append(diviseur)
            n //= diviseur
        diviseur += 1
    if n > 1:
        resultat.append(n)
    return resultat


def fibonacci_recursif(n: int) -> int:
    """Calcule F(n) en suivant la définition récursive."""
    if n < 0:
        raise ValueError("n doit être positif ou nul")
    if n < 2:
        return n
    return fibonacci_recursif(n - 1) + fibonacci_recursif(n - 2)


def fibonacci(n: int) -> int:
    """Calcule F(n) avec une boucle et deux variables."""
    if n < 0:
        raise ValueError("n doit être positif ou nul")

    precedent, courant = 0, 1
    for _ in range(n):
        precedent, courant = courant, precedent + courant
    return precedent


def euclide_etendu(a: int, b: int) -> tuple[int, int, int]:
    """Renvoie (pgcd, u, v) tel que a*u + b*v = pgcd."""
    if b == 0:
        return abs(a), 1 if a >= 0 else -1, 0

    pgcd_resultat, u, v = euclide_etendu(b, a % b)
    return pgcd_resultat, v, u - (a // b) * v


def puissance_mod_naive(a: int, e: int, n: int) -> int:
    """Calcule a**e modulo n avec e multiplications."""
    if e < 0 or n <= 0:
        raise ValueError("e doit être positif et n strictement positif")

    resultat = 1
    for _ in range(e):
        resultat = resultat * a % n
    return resultat


def puissance_mod(a: int, e: int, n: int) -> int:
    """Calcule a**e modulo n par exponentiation rapide."""
    if e < 0 or n <= 0:
        raise ValueError("e doit être positif et n strictement positif")

    resultat = 1
    base = a % n
    while e > 0:
        if e % 2 == 1:
            resultat = resultat * base % n
        base = base * base % n
        e //= 2
    return resultat


if __name__ == "__main__":
    tp2().run()
