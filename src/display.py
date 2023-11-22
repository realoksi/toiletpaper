import asyncio
import curses
from typing import Callable, Tuple


# events = {curses.KEY_UP: [myfunction, myotherfunction]}


# x, y
class Navigator:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        strict: bool = False,
        bounds: Tuple[
            Tuple[int, int], Tuple[int, int]
        ] = None,  # bounds is ((minimum x, y), and (maximum x, y))
    ) -> None:
        self.x = x
        self.x_origin = x
        self.y = y
        self.y_origin = x

        self.strict = strict
        self.bounds = bounds

    def x_within(self) -> bool:
        return self.x >= self.bounds[0][0] and self.x <= self.bounds[1][0]

    def y_within(self) -> bool:
        return self.y >= self.bounds[0][1] and self.y <= self.bounds[1][1]

    def within(self) -> bool:
        return self.x_within() and self.y_within()

    def reset(self):
        self.x = self.x_origin
        self.y = self.y_origin

    def up(self, distance: int = 1):
        self.y -= distance

        if self.strict:
            if not self.y_within():
                self.y += distance

    def down(self, distance: int = 1):
        self.y += distance

        if self.strict:
            if not self.y_within():
                self.y -= distance

    def left(self, distance: int = 1):
        self.x -= distance

        if self.strict:
            if not self.x_within():
                self.x += distance

    def right(self, distance: int = 1):
        self.x += distance

        if self.strict:
            if not self.x_within():
                self.x -= distance


class AsyncDisplay:
    def __init__(self, stdscr, cursor: int = 0):
        self.stdscr = stdscr
        self.ok = False
        self.events = dict()

        self.navigator = Navigator()

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
                        self.navigator.up()
                    case curses.KEY_DOWN:
                        self.navigator.down()
                    case curses.KEY_LEFT:
                        self.navigator.left()
                    case curses.KEY_RIGHT:
                        self.navigator.right()

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
