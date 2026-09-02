# -*- coding: utf-8 -*-
"""Ponto de entrada: `python -m responsa` ou comando `responsa` (após instalado)."""
from . import menu


def main() -> None:
    try:
        menu.main_loop()
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")


if __name__ == "__main__":
    main()
