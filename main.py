"""Ponto de entrada do RentSmart. Execute com:  python main.py"""

import sys

from rentsmart.interface import InterfaceTerminal


def main() -> None:
    # Garante acentuação correta no terminal do Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        InterfaceTerminal().executar()
    except (KeyboardInterrupt, EOFError):
        print("\nExecução encerrada pelo usuário.")


if __name__ == "__main__":
    main()
