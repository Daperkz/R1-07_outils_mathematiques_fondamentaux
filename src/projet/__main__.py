# ==============================================================================
# Projet - Outils Mathématiques Fondamentaux
# August CONCHIN
# Louay BEN AHMED
#
# __main__
# ==============================================================================

import sys

from .app import App


def main() -> int:
    return App().run()


if __name__ == "__main__":
    sys.exit(main())
