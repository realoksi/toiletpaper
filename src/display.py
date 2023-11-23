import asyncio
import curses
from typing import Callable

from navigator import Navigator


class AsyncDisplay:
    def __init__(self, stdscr, cursor: int = 0):
        self.stdscr = stdscr
        self.ok = False
        self.events = dict()

        self.navigator = Navigator(
            origin=[0, 0], strict=True, limits=([0, 0], [24, 24])
        )

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)

        self.stdscr.nodelay(True)

        curses.curs_set(cursor)

    def event(self, constant: int, action: Callable[["AsyncDisplay"], None]):
        self.events[constant] = action
        return self

    @property
    def ok(self):
        return self._ok

    @ok.setter
    def ok(self, value):
        self._ok = value

    async def loop(
        self,
        pre: Callable[["AsyncDisplay"], None] = None,
        post: Callable[["AsyncDisplay"], None] = None,
    ) -> None:
        """
        :param pre:
        :param post:
        :return: None
        """
        self.ok = True
        while self.ok:
            self.stdscr.clear()
            if pre:
                pre(self)

            ch = self.stdscr.getch()

            if ch in self.events:
                self.events[ch](self)
            else:
                match ch:
                    case curses.KEY_UP:
                        self.navigator.move(0, -1)
                    case curses.KEY_DOWN:
                        self.navigator.move(0, 1)
                    case curses.KEY_LEFT:
                        self.navigator.move(1, -1)
                    case curses.KEY_RIGHT:
                        self.navigator.move(1, 1)

            curses.flushinp()  # We'll need to flush the input queue after we process input on every iteration. Should we not do this, it enables a user to be able to queue too many keys, and processing of entries in that queue will drastically backup the script.

            if post:
                post(self)

            self.stdscr.refresh()

            await asyncio.sleep(
                0.03
            )  # 300ms should be more than enough. This keeps the process CPU usage from unecessarily jumping


class Option:
    def __init__(
        self, label: str, action: Callable[[], None] = None, attributes=curses.A_NORMAL
    ) -> None:
        self.label = label
        self.action = action
        self.attributes = attributes
