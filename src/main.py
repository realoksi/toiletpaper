import random
from typing import Callable
import curses

REFRESH_LIFETIME = 1000
FRUITS = [
    "Apple",
    "Banana",
    "Cherry",
    "Date",
    "Elderberry",
    "Orange",
    "Fig",
    "Grape",
    "Mango",
    "Honeydew",
    "Kiwi",
    "Lemon",
    "Lime",
]


class state:
    def __init__(self, title: str, callback: Callable[[], None] = None) -> None:
        self._title = title
        self._callback = callback

    @property
    def title(self) -> str:
        return self._title

    @property
    def callback(self):
        return None if not self._callback else self._callback


"""
    A multi-state class allows for storing and managing a sequentially-iteratable
    list of states. It can work with 1 up-to whatever the maximum amount of
    items a list can store at a single time.

    Note that multistate.callback() will never execute the callback, it only
    return a reference to the callback. Executing the callback must be the
    responsibility of the original caller.
"""


class multistate:
    def __init__(self, states: list[state] = list()) -> None:
        self.states = states

    def forward(self) -> None:
        self.states.append(self.states.pop(0))

    @property
    def title(self):
        return self.states[0].title

    @property
    def callback(self):
        return self.states[0].callback


# below is all trash garbage poopoo


def main(stdscr):
    stdscr.nodelay(True)

    curses.curs_set(0)

    options = [
        multistate([state("Hello"), state("World!")]),
        state("Quit", exit),
    ]

    refresh_age = 0
    fruit = random.choice(FRUITS)
    highlight = 0

    while 1:
        stdscr.clear()

        if REFRESH_LIFETIME < refresh_age:
            refresh_age = 0
            # ... Any values that needs to be updated at lower intervals
            # should go here.
            fruit = random.choice(FRUITS)
        else:
            refresh_age += 1

        stdscr.addstr(
            0,
            0,
            fruit,
        )

        stdscr.addstr(
            1,
            0,
            "REFRESH_LIFETIME="
            + str(REFRESH_LIFETIME)
            + ", refresh_age="
            + str(refresh_age),
        )

        # render all available options
        for i, e in enumerate(options):
            if i == highlight:
                stdscr.addstr(i + 3, 0, e.title, curses.A_STANDOUT)
            else:
                stdscr.addstr(i + 3, 0, e.title)

        ch = stdscr.getch()

        match ch:
            case curses.KEY_UP:
                highlight = max(0, highlight - 1)
            case curses.KEY_DOWN:
                highlight = min(len(options) - 1, highlight + 1)
            case _:
                if ch == ord("\n"):
                    if options[highlight].callback:
                        options[highlight].callback()

                    if isinstance(options[highlight], multistate):
                        options[highlight].forward()

        stdscr.refresh()


curses.wrapper(main)()
