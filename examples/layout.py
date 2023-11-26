import curses
from threading import Thread
import time
import random
from typing import Any, Callable, List


class Window:
    def __init__(
        self,
        window,
        callback: Callable[[Any, int], None] = None,
    ):
        self.window = window
        self.callback = callback
        self.windows: List[Window] = None

    def render(self, ch: int = None):
        if self.windows:
            for window in self.windows:
                window.render(ch=ch)
        else:
            self.window.clear()

            if self.callback:
                self.callback(self.window, ch)

            self.window.refresh()

    def split(
        self, direction: str = "horizontal", clear_callback: bool = True
    ) -> List["Window"]:
        if self.windows:
            return -1

        begin_y, begin_x = self.window.getbegyx()
        nlines, ncols = self.window.getmaxyx()

        # TODO: Allow specification of sizes on split. Perhaps specification of the
        # first window (left, or top) size, and the second will fill the remainder.

        self.windows = []

        if direction == "horizontal":
            self.windows.append(Window(curses.newwin(nlines, ncols // 2, begin_y, 0)))
            self.windows.append(
                Window(
                    curses.newwin(
                        nlines,
                        (ncols // 2) + 1 if (ncols % 2) else ncols // 2,
                        begin_y,
                        ncols // 2,
                    )
                )
            )
        elif direction == "verticle":
            self.windows.append(Window(curses.newwin(nlines // 2, ncols, 0, begin_x)))
            self.windows.append(
                Window(
                    curses.newwin(
                        (nlines // 2) + 1 if (nlines % 2) else nlines // 2,
                        ncols,
                        nlines // 2,
                        begin_x,
                    )
                )
            )
        else:
            return -1

        if clear_callback:
            self.callback = None
        return self.windows


class Layout(Thread):
    def __init__(
        self,
        stdscr,
        callback: Callable[["Window", int], None] = None,
        exit_key: int = curses.KEY_DC,
        wait: float = 0.037,
    ):
        Thread.__init__(self)

        self.exit_key = exit_key
        self.wait = wait

        self.window = Window(stdscr, callback)

        self.ok = 1

        self.window.window.nodelay(1)

        curses.curs_set(0)

    def run(self):
        while self.ok:
            ch = self.window.window.getch()

            match ch:
                case self.exit_key:
                    self.ok = 0
                case curses.KEY_PPAGE:
                    self.wait += 0.01
                case curses.KEY_NPAGE:
                    self.wait -= 0.01

            curses.flushinp()

            self.window.render(ch)

            time.sleep(self.wait)


import datetime
import threading


def about_callback(window, ch):
    now = datetime.datetime.now().replace(microsecond=0).isoformat()

    window.addstr(0, 0, f"Window: '{type(window)}' at '{hex(id(window)).capitalize()}'")
    window.addstr(1, 0, f"Date and time: {now}")

    if ch == -1:
        window.addstr(2, 0, "Input status: None")
    else:
        window.addstr(2, 0, f"Input status: {ch}")

    window.addstr(3, 0, "List of threads:")

    for index, thread in enumerate(threading.enumerate()):
        if thread.is_alive():
            window.addstr(index + 4, 0, f"+ {thread.name.lower()} <id:{thread.ident}>")
        else:
            window.addstr(index + 4, 0, f"- {thread.name.lower()} <id:{thread.ident}>")

    window.addstr(index + 5, 0, "Press the 'end' key to stop the application.")


def main(stdscr):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    stdscr.bkgd(" ", curses.color_pair(random.randrange(1, 8)))

    layout = Layout(
        stdscr=stdscr,
        wait=0.0475,
        exit_key=curses.KEY_END,
    )

    layout.window.split("horizontal")

    layout.window.windows[1].callback = about_callback
    layout.window.windows[1].window.bkgd(" ", curses.color_pair(random.randrange(1, 8)))

    layout.window.windows[0].split("verticle")

    for window in layout.window.windows[0].windows:
        window.window.bkgd(" ", curses.color_pair(random.randrange(1, 8)))

    layout.window.windows[0].windows[0].callback = about_callback
    layout.window.windows[0].windows[1].callback = about_callback

    layout.start()

    layout.join()


if __name__ == "__main__":
    curses.wrapper(main)
