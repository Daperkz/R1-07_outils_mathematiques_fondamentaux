# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
# Sami BEN SLIMA
#
# __main__
# ==============================================================================

import sys

from .app import App


def main() -> int:
    """Crée l'application et lance sa boucle graphique."""
    return App().run()


if __name__ == "__main__":
    sys.exit(main())
