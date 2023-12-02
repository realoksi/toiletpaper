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
                window.render(ch)
        else:
            self.window.erase()

            if self.callback:
                self.callback(self.window, ch)

            self.window.refresh()

    # When resizing, we SHOULD account for the position and size of the children
    # windows in 'self.windows'. Optionally, 
    def resize(self, y, x, inherit:bool=True):
        pass

    def move(self, y, x, inherit:bool=True):
        pass

    def split(
        self,
        columns: int = 0,
        verticle: bool = False,
        lines: int = 0,
        callbacks: List[Callable[[Any, int], None]] = None,
    ) -> (List["Window"], None):
        if self.windows:
            return

        # NOTE: By performing a floored division on either nlines or ncols, there's a potential for
        # a single column or line to be missed, leaving whichever blank. A temporary solution is to
        # perform the floored division, and add one to the result of the division only when the
        # original value of ncols or nlines isn't evenly divisible by 2.

        begin_y, begin_x = self.window.getbegyx()
        max_y, max_x = self.window.getmaxyx()

        nlines = lines if lines else max_y // 2
        ncols = columns if columns else max_x // 2

        self.windows = [
            Window(curses.newwin(nlines, max_x, begin_y, begin_x), callbacks[0]),
            Window(
                curses.newwin(
                    max_y - nlines if lines else max_y // 2,
                    max_x,
                    nlines,
                    begin_x,
                ),
                callbacks[1],
            ),
        ] if verticle else [
            Window(curses.newwin(max_y, ncols, begin_y, begin_x), callbacks[0]),
            Window(
                curses.newwin(
                    max_y,
                    max_x - columns if columns else max_x // 2,
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
                    self.resize(*self.window.getmaxyx())

            curses.flushinp()

            self.render(ch)

            time.sleep(self.wait)


import datetime
import threading

def statusbar_callback(window, ch):
    window.addstr(
        0,
        0,
        "🗃️ File ✍️ Edit 🔍 Search ❓ Help",
    )

def browser_callback(window, ch):
    window.addstr(1, 0, "未来茶屋 vol.0 - EP")
    window.addstr(2, 1, "白猫海賊船 (feat. 日南結里)")
    window.addstr(3, 1, "ゲームオーバー (feat. TORIENA)", curses.A_STANDOUT)
    window.addstr(4, 1, "コットンキャンディ・シープ・ナイト")
    window.addstr(5, 1, "アルケの悲しみ -Bitter Ver.-")
    window.addstr(6, 1, "プリズム")
    window.addstr(7, 1, "くいしんぼハッカー (feat. くいしんぼあかちゃん)")

def info_callback(window, ch):
    window.addstr(1, 1, "File Name: 02 ゲームオーバー (feat. TORIENA).m4a")
    window.addstr(2, 1, "File Size: 7.93 MB (8 322 602 bytes)")
    window.addstr(3, 1, "Last Modified: 2023-11-10 01:03:58")
    window.addstr(4, 1, "Duration: 3:52.609 (10 258 045 samples)")
    window.addstr(5, 1, "Bitrate: 266 kbps")
    window.addstr(5, 1, "Codec: AAC")

def main(stdscr):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    layout = Layout(stdscr)

    layout.split(verticle=True, lines=1, callbacks=[statusbar_callback, None])

    statusbar = layout.windows[0]

    content = layout.windows[1]

    content.split(callbacks=[browser_callback, info_callback])

    layout.start()

    layout.join()


if __name__ == "__main__":
    curses.wrapper(main)
