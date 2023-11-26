import curses
from threading import Thread
import time
import random
from typing import List

# option navigator, not positional navigator

# Verticle Navigation (Scrollable, Non-scrollable)
#
# Option 1
# Option 2 <
# Option 3
#
# KEY_UP
#
# Option 1 <
# Option 2
# Option 3
#
# Horizontal Navigation (Scrollable, None-scrollable)


class Option:
    def __init__(self, label: str, action=None, attributes=curses.A_NORMAL) -> None:
        self.label = label
        self.action = action
        self.attributes = attributes


class Navigator:
    def __init__(self, options: List[Option]):
        self.options = options
        self.index = 0

    def reset(self):
        self.index = 0

    def next(self, distance: int = 1) -> Option:
        self.index += distance

        if self.index >= len(self.options) or self.index < 0:
            self.index -= distance

        return self[self.index]

    def previous(self, distance: int = 1) -> Option:
        return self.next(distance * -1)

    def __getitem__(self, index):
        return self.options[index]


"""
    set of options
    index (when down, index+, when up index-) keep within bounds of options
"""


class Display(Thread):
    def __init__(self, stdscr, thread_name: str | None = None):
        Thread.__init__(self, name=thread_name)

        stdscr.nodelay(1)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)

        self.windows = {"stdscr": stdscr}
        self.ok = 1

    def run(self):
        stdscr = self.windows["stdscr"]

        tmp_nav = Navigator(
            [
                Option("Option 1"),
                Option("Option 2"),
                Option("Option 3"),
                Option("Option 4"),
                Option("Option 5"),
                Option("Option 6"),
                Option("Option 7"),
                Option("Option 8"),
                Option("Option 9"),
                Option("Option 10"),
            ]
        )

        stdscr.bkgd(" ", curses.color_pair(1))
        while self.ok:
            stdscr.clear()

            stdscr.addstr(
                0,
                0,
                f"curses.LINES={curses.LINES}, curses.COLS={curses.COLS}, random.randint={random.randint(0, 9)}",
            )

            ch = stdscr.getch()

            match ch:
                case curses.KEY_UP:
                    tmp_nav.previous()
                case curses.KEY_DOWN:
                    tmp_nav.next()
                case _:
                    if ch == ord("\n"):
                        self.ok = 0

            for index, option in enumerate(tmp_nav):
                attributes = option.attributes
                if index == tmp_nav.index:
                    attributes |= curses.A_STANDOUT

                stdscr.addstr(index + 1, 0, option.label, attributes)

            curses.flushinp()

            stdscr.refresh()
            time.sleep(0.03)


def main(stdscr):
    display = Display(stdscr)

    display.start()

    display.join()


if __name__ == "__main__":
    curses.wrapper(main)
