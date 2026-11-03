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
    """La fonction principale qui démarre le projet"""
    return App().run()


if __name__ == "__main__":
    sys.exit(main())
