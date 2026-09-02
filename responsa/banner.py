# -*- coding: utf-8 -*-
"""
banner.py
---------
Exibe o banner do RESPONSA: um "olho de coruja" em ASCII art, colorido,
mostrado sempre que o programa é iniciado no terminal.
"""
from rich.console import Console
from rich.text import Text

console = Console()

# Olho de coruja estilizado em ASCII art.
OWL_EYE = r"""
                  .:^~7?JY55PGGGGP5YJ7~^:.
              .^7Y5GB###&&&&&&&&&&&&###BG5Y7^.
           :~YG#&&&&&&&&&&&&&&&&&&&&&&&&&&&&#GY~:
        :?P&&&&&&&&&&&&&#GPYJ?77?JYPG#&&&&&&&&&&&&P?:
      ^Y#&&&&&&&&&#PY7~:.            .:~7YP#&&&&&&&&&&#Y^
    ^5&&&&&&&&#P7^.        .:^~~~~^:.        .^7P#&&&&&&&&5^
   J&&&&&&&&G7.        :~JG#&&&&&&&&#GJ~:        .7G&&&&&&&&J
  P&&&&&&&B7.        ^Y#&&&&&&&&&&&&&&&&#Y^        .7B&&&&&&&P
 G&&&&&&&5.        ^P&&&&&&&&&&&&&&&&&&&&&&P^        .5&&&&&&&G
Y&&&&&&&5        .Y&&&&&&&&&#GPPPPG#&&&&&&&&&Y.        5&&&&&&&Y
#&&&&&&&5       .P&&&&&&&B?:        :?B&&&&&&&P.       5&&&&&&&#
#&&&&&&&P       J&&&&&&&5.    ^7JJ7^    5&&&&&&&J      P&&&&&&&#
5&&&&&&&&:     .#&&&&&&#.   ^P&&&&&&P^   #&&&&&&#.    :&&&&&&&&5
 #&&&&&&&B:    5&&&&&&&J   .#&&&&&&&&#.  J&&&&&&&5   :B&&&&&&&#
 :#&&&&&&&&Y^.J&&&&&&&&:   Y&&&&&&&&&&Y   :&&&&&&&&J.^Y&&&&&&&&#:
  :G&&&&&&&&&&&&&&&&&&&:  .#&&&&&&&&&&#.  :&&&&&&&&&&&&&&&&&&&G:
   .Y&&&&&&&&&&&&&&&&&&P  :&&&&&&&&&&&&:  P&&&&&&&&&&&&&&&&&Y.
     7B&&&&&&&&&&&&&&&&&7 ^#&&&&&&&&&&#^ 7&&&&&&&&&&&&&&&&B7
      .7G&&&&&&&&&&&&&&&&Y^7G&&&&&&&&G7^Y&&&&&&&&&&&&&&&G7.
         ~JB&&&&&&&&&&&&&&&P7~^^^^~7P&&&&&&&&&&&&&&&&BJ~
             ^7YG#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&#GY7^
                  .:~7JYPGB#&&&&&&&&#BGPYJ7~:.
"""

TITLE = r"""
██████╗ ███████╗███████╗██████╗  ██████╗ ███╗   ██╗███████╗ █████╗
██╔══██╗██╔════╝██╔════╝██╔══██╗██╔═══██╗████╗  ██║██╔════╝██╔══██╗
██████╔╝█████╗  ███████╗██████╔╝██║   ██║██╔██╗ ██║███████╗███████║
██╔══██╗██╔══╝  ╚════██║██╔═══╝ ██║   ██║██║╚██╗██║╚════██║██╔══██║
██║  ██║███████╗███████║██║     ╚██████╔╝██║ ╚████║███████║██║  ██║
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
"""

# Gradiente de cores que "varre" o olho de cima a baixo, dando o efeito
# colorido pedido (sem depender de libs extras além do rich).
GRADIENT = [
    "bright_black", "grey37", "purple4", "medium_purple3", "slate_blue3",
    "royal_blue1", "deep_sky_blue1", "cyan1", "spring_green2", "green1",
    "yellow1", "orange1", "red1", "magenta1", "purple",
]


def print_banner(subtitle: str = "OSINT Toolkit") -> None:
    """Imprime o olho de coruja colorido + título + subtítulo."""
    console.clear()
    lines = OWL_EYE.splitlines()
    n = max(len(lines) - 1, 1)
    for i, line in enumerate(lines):
        if not line.strip():
            console.print("")
            continue
        color = GRADIENT[int(i / n * (len(GRADIENT) - 1))]
        console.print(Text(line, style=f"bold {color}"), justify="center")

    console.print(Text(TITLE, style="bold cyan"), justify="center")
    console.print(
        Text(f"— {subtitle} —", style="italic bright_white"), justify="center"
    )
    console.print(
        Text(
            "Uso ético e responsável apenas. Consulte a LGPD antes de usar.",
            style="dim",
        ),
        justify="center",
    )
    console.print()


if __name__ == "__main__":
    print_banner()
