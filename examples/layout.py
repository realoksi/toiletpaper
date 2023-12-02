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
            self.window.erase()

            if self.callback:
                self.callback(self.window, ch)

            self.window.refresh()

    # When the window is resized, we could try to go off the original value
    # for the position of the lower-right cell of that window.
    def resize(self):
        pass

    def split(
        self,
        columns: int = 0,
        verticle: bool = False,
        lines: int = 0,
        callbacks: List[Callable[[Any, int], None]] = None,
    ) -> (List["Window"], None):
        if self.windows:
            return -1

        # NOTE: By performing a floored division on either nlines or ncols, there's a potential for
        # a single column or line to be missed, leaving whichever blank. A temporary solution is to
        # perform the floored division, and add one to the result of the division only when the
        # original value of ncols or nlines isn't evenly divisible by 2.

        begin_y, begin_x = self.window.getbegyx()
        max_y, max_x = self.window.getmaxyx()

        if verticle:
            nlines = lines if lines else max_y // 2

            self.windows = [
                Window(curses.newwin(nlines, max_x, begin_y, begin_x), callbacks[0]),
                Window(
                    curses.newwin(
                        (max_y - nlines) if lines else max_y // 2,
                        max_x,
                        nlines,
                        begin_x,
                    ),
                    callbacks[1],
                ),
            ]
        else:
            ncols = columns if columns else max_x // 2

            self.windows = [
                Window(curses.newwin(max_y, ncols, begin_y, begin_x), callbacks[0]),
                Window(
                    curses.newwin(
                        max_y,
                        (max_x - columns) if columns else max_x // 2,
                        begin_y,
                        ncols,
                    ),
                    callbacks[1],
                ),
            ]

        self.callback = None

        return self.windows


class Layout(Thread, Window):
    def __init__(
        self,
        stdscr,
        callback: Callable[[Any, int], None] = None,
        exit_key: int = curses.KEY_DC,
        wait: float = 0.037,
    ):
        Thread.__init__(self)
        Window.__init__(self, window=stdscr, callback=callback)

        self.exit_key = exit_key
        self.wait = wait
        self.ok = 1

        self.window.nodelay(1)

        curses.curs_set(0)

    def run(self):
        while self.ok:
            ch = self.window.getch()

            match ch:
                case self.exit_key:
                    self.ok = 0
                case curses.KEY_PPAGE:
                    self.wait += 0.01
                case curses.KEY_NPAGE:
                    self.wait -= 0.01
                case curses.KEY_RESIZE:
                    # Move your mom with window.mvwin
                    # We should be able to move everything to their new
                    # positions without a crash occurring? Maybe we can
                    # check if a window is at a specific line+column.
                    # fuck your mom with window.resize
                    pass

            curses.flushinp()

            self.render(ch)

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

    window.addstr(index + 5, 0, "Press the 'delete' key to stop the application.")


def statusbar_callback(window, ch):
    window.addstr(
        0,
        0,
        "🗃️ File ✍️ Edit 🔍 Search ❓ Help",
    )


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

    layout = Layout(stdscr)

    layout.split(verticle=True, lines=1, callbacks=[statusbar_callback, None])

    statusbar = layout.windows[0]

    statusbar.window.bkgd(" ", curses.color_pair(1))

    content = layout.windows[1]

    content.split(callbacks=[about_callback, about_callback])

    left_content = content.windows[0]
    left_content.window.bkgd(" ", curses.color_pair(5))

    right_content = content.windows[1]
    right_content.window.bkgd(" ", curses.color_pair(4))

    layout.start()

    layout.join()


if __name__ == "__main__":
    curses.wrapper(main)
