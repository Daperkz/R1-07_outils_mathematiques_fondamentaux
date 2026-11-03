# ==============================================================================
# tp - Outils Mathématiques Fondamentaux
# August CONCHIN
#
# tp3 - Polynômes et fonctions
# ==============================================================================

from typing import Callable, Tuple

import time


class tp3:
    def __init__(self) -> None:
        self.exercices: dict[str, Callable] = {
            "1": self.getExercice1,
            "2.1": self.getExercice2_1,
            "2.2": self.getExercice2_2,
            "2.3": self.getExercice2_3,
            "3": self.getExercice3,
            "4.1": self.getExercice4_1,
            "4.3": self.getExercice4_3,
            "4.4": self.getExercise4_4,
            "5.1": self.getExercise5_1,
            "6.1": self.getExercise6_1,
            "6.2": self.getExercise6_2,
            "7.1": self.getExercise7_1,
            "8.1": self.getExercise8_1,
            "8.2": self.getExercise8_2,
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

    def getExercice1(self) -> int:
        print(evaluate_naif([2, 3, 0, 5], 2))
        print(evaluate_naif([2, 3, 0, 5], 0))
        return 0

    def getExercice2_1(self) -> int:
        P: list[float] = [2, 3, 0, 5]
        for x in (-2, 0, 1, 2, 10):
            print(x, evaluate_naif(P, x), evaluate(P, x))
        return 0

    def getExercice2_2(self) -> int:
        P: list[float] = [2.0, 3.0, 0.0, 5.0]

        for degre in (1000, 5000, 20000):
            P = [1] * (degre + 1)
            debut = time.perf_counter()
            a = evaluate_naif(P, 1.0001)
            t_naif = time.perf_counter() - debut
            debut = time.perf_counter()
            b = evaluate(P, 1.0001)
            t_horner = time.perf_counter() - debut
            print(
                f"degre {degre:>6} : naif {t_naif:.5f}"
                f"s | horner {t_horner:.5f} s "
                f"| rapport {t_naif / t_horner:.1f} | "
                f"ecart des valeurs {abs(a - b):.2e}"
            )
        return 0

    def getExercice2_3(self) -> int:
        P: list[float] = [2.0, 3.0, 0.0, 5.0]

        for degre in (200, 400, 800):
            P = [1] * (degre + 1)
            debut = time.perf_counter()
            a = evaluate_naif(P, 3)
            t_naif = time.perf_counter() - debut
            debut = time.perf_counter()
            b = evaluate(P, 3)
            t_horner = time.perf_counter() - debut
            print(
                f"degre {degre:>4} : rapport {t_naif / t_horner:.1f}"
                f" | resultats egaux : {a == b}"
            )
        return 0

    def getExercice3(self) -> int:
        P1: list[float] = [2.0, 3.0, 0.0, 5.0]
        P2: list[float] = [9.2]

        print(deriver(P1))
        print(deriver(P2))
        return 0

    def getExercice4_1(self) -> int:
        racine: float = dichotomy(pow2_min_2, 0, 2)

        print(racine)
        print(abs(racine - 2 ** 0.5) < 1e-9)
        return 0

    def getExercice4_2(self) -> int:

        Q: list[float] = [-5.0, -2.0, 0.0, 1.0]
        racine, tours = newton(Q, 2)
        print(racine, "en", tours, "tours")
        print(abs(evaluate(Q, racine)) < 1e-10)
        return 0

    def getExercice4_3(self) -> int:
        R: list[float] = [2, -2, 0, 1]
        print(newton_trace(R, 0, 8))
        try:
            print(newton(R, 0))
        except RuntimeError as erreur:
            print("echec :", erreur)
            return 1
        return 0

    def getExercise4_4(self) -> int:
        polynomial: list[float] = [-5.0, -2.0, 0.0, 1.0]
        for start in (2.0, 0.0):
            try:
                root: float
                iterations: int
                root, iterations = newton(polynomial, start)
                print(
                    f"Depart {start} : racine {root}, {iterations} iterations"
                )
            except RuntimeError as error:
                print(f"Depart {start} : echec - {error}")
        return 0

    def getExercise5_1(self) -> int:
        import matplotlib.pyplot as plt

        Q: list[float] = [-5, -2, 0, 1]          # x^3 - 2x - 5
        xs: list[float] = [i / 100 for i in range(-300, 301)]
        ys: list[float] = [evaluate(Q, x) for x in xs]

        plt.figure()
        plt.plot(xs, ys, label="x^3 - 2x - 5")
        plt.axhline(0, linewidth=0.8)
        plt.axvline(0, linewidth=0.8)
        plt.ylim(-20, 20)
        plt.xlabel("x")
        plt.ylabel("P(x)")
        plt.legend()
        plt.title("Un polynome et son unique racine reelle")
        plt.show()
        return 0

    def getExercise6_1(self) -> int:
        print("Somme :", add_polynomials([1.0, 1.0], [1.0, 1.0]))
        print("Produit :", multiply_polynomials([1.0, 1.0], [1.0, 1.0]))
        print(
            "Difference de carres :",
            multiply_polynomials([-1.0, 1.0], [1.0, 1.0])
        )
        return 0

    def getExercise6_2(self) -> int:
        result: list[float] = [1.0]
        for _ in range(10):
            result = multiply_polynomials(result, [1.0, 1.0])
        print(result)
        return 0

    def getExercise7_1(self) -> int:
        exact_derivative: float = cosine_approx(1.0)
        for step in (1e-1, 1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12):
            forward_error: float = abs(
                forward_difference(sine_approx, 1.0, step) - exact_derivative
            )
            centered_error: float = abs(
                central_difference(sine_approx, 1.0, step) - exact_derivative
            )
            print(
                f"h={step:.0e} : erreur avant {forward_error:.2e} | "
                f"erreur centree {centered_error:.2e}"
            )
        return 0

    def getExercise8_1(self) -> int:
        for subdivisions in (10, 100, 1000):
            rectangle_result: float = rectangles(square, 0.0, 1.0, subdivisions)
            trapezoid_result: float = trapezoids(square, 0.0, 1.0, subdivisions)
            simpson_result: float = simpson(square, 0.0, 1.0, subdivisions)
            print(
                f"n={subdivisions} : erreur rectangles "
                f"{abs(rectangle_result - 1 / 3):.2e} | trapezes "
                f"{abs(trapezoid_result - 1 / 3):.2e} | Simpson "
                f"{abs(simpson_result - 1 / 3):.2e}"
            )
        return 0

    def getExercise8_2(self) -> int:
        function: Callable[[float], float] = lambda value: (
            4.0 / (1.0 + value * value)
        )
        pi_approximation: float = 3.141592653589793
        trapezoid_result: float = trapezoids(function, 0.0, 1.0, 1000)
        simpson_result: float = simpson(function, 0.0, 1.0, 1000)
        print(
            f"Trapezes : {trapezoid_result:.12f},"
            f" erreur {abs(trapezoid_result - pi_approximation):.2e}"
        )
        print(
            f"Simpson : {simpson_result:.12f},"
            f" erreur {abs(simpson_result - pi_approximation):.2e}"
        )
        return 0


def evaluate_naif(P: list[float], x: float) -> float:
    retv: float = 0.0
    for i in range(len(P)):
        retv += P[i] * (x ** i)
    return retv


def evaluate(P: list[float], x: float) -> float:
    retv: float = 0.0
    for coef in reversed(P):
        retv = retv * x + coef
    return retv


def deriver(P: list[float]) -> list[float]:
    if len(P) <= 1:
        return [0.0]
    return [i * P[i] for i in range(1, len(P))]


def dichotomy(
        f: Callable, a: float, b: float, tolerance: float = 1e-12
        ) -> float:
    fa, fb = f(a), f(b)
    if (fa == 0):
        return a
    if fb == 0:
        return b
    if fa * fb > 0:
        raise ValueError("f(a) et f(b) doivent etre de signes opposes")
    while b - a > tolerance:
        milieu = (a + b) / 2
    if f(a) * f(milieu) <= 0:
        b = milieu
    else:
        a = milieu
    return (a + b) / 2


def pow2_min_2(x: float) -> float:
    return x * x - 2


def newton(
        P: list[float],
        start: float,
        tolerance: float = 1e-12,
        max_round: int = 100
        ) -> Tuple[float, int]:
    derivee: list[float] = deriver(P)
    x: float = start
    for tour in range(max_round):
        valeur = evaluate(P, x)
        pente = evaluate(derivee, x)
        if pente == 0:
            raise ZeroDivisionError(
                "tangente horizontale, Newton ne peut pas continuer"
            )
        suivant = x - valeur / pente
        if abs(suivant - x) <= tolerance * max(1.0, abs(suivant)):
            return suivant, tour + 1
        x = suivant
    raise RuntimeError("pas de convergence en {} tours".format(max_round))


def newton_trace(P: list[float], depart: float, tours: int) -> list[float]:
    derivee = deriver(P)
    x = float(depart)
    trajet = [x]
    for _ in range(tours):
        pente = evaluate(derivee, x)
        if pente == 0:
            break
        x = x - evaluate(P, x) / pente
        trajet.append(x)
    return trajet


def add_polynomials(first: list[float], second: list[float]) -> list[float]:
    length: int = max(len(first), len(second))
    result: list[float] = []
    for index in range(length):
        first_coefficient: float = first[index] if index < len(first) else 0.0
        second_coefficient: float = (
            second[index] if index < len(second) else 0.0
        )
        result.append(first_coefficient + second_coefficient)
    return result or [0.0]


def multiply_polynomials(
        first: list[float], second: list[float]
        ) -> list[float]:
    if not first or not second:
        return [0.0]
    result: list[float] = [0.0] * (len(first) + len(second) - 1)
    for first_degree, first_coefficient in enumerate(first):
        for second_degree, second_coefficient in enumerate(second):
            result[first_degree + second_degree] += (
                first_coefficient * second_coefficient
            )
    return result


def sine_approx(value: float) -> float:
    result: float = value
    term: float = value
    for index in range(1, 12):
        term *= -(value * value) / ((2 * index) * (2 * index + 1))
        result += term
    return result


def cosine_approx(value: float) -> float:
    result: float = 1.0
    term: float = 1.0
    for index in range(1, 12):
        term *= -(value * value) / ((2 * index - 1) * (2 * index))
        result += term
    return result


def forward_difference(
        function: Callable[[float], float], value: float, step: float
        ) -> float:
    if step <= 0:
        raise ValueError("step doit etre positif")
    return (function(value + step) - function(value)) / step


def central_difference(
        function: Callable[[float], float], value: float, step: float
        ) -> float:
    if step <= 0:
        raise ValueError("step doit etre positif")
    return (function(value + step) - function(value - step)) / (2 * step)


def rectangles(
        function: Callable[[float], float],
        start: float,
        end: float,
        subdivisions: int
        ) -> float:
    if subdivisions <= 0:
        raise ValueError("subdivisions doit etre positif")
    step: float = (end - start) / subdivisions
    total: float = 0.0
    for index in range(subdivisions):
        total += function(start + index * step)
    return total * step


def trapezoids(
        function: Callable[[float], float],
        start: float,
        end: float,
        subdivisions: int
        ) -> float:
    if subdivisions <= 0:
        raise ValueError("subdivisions doit etre positif")
    step: float = (end - start) / subdivisions
    total: float = (function(start) + function(end)) / 2
    for index in range(1, subdivisions):
        total += function(start + index * step)
    return total * step


def simpson(
        function: Callable[[float], float],
        start: float,
        end: float,
        subdivisions: int
        ) -> float:
    if subdivisions <= 0 or subdivisions % 2 != 0:
        raise ValueError("subdivisions doit etre un entier positif pair")
    step: float = (end - start) / subdivisions
    total: float = function(start) + function(end)
    for index in range(1, subdivisions):
        coefficient: int = 4 if index % 2 == 1 else 2
        total += coefficient * function(start + index * step)
    return total * step / 3


def square(value: float) -> float:
    return value * value


if __name__ == "__main__":
    tp3().run()
