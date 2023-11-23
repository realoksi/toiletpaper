import asyncio
import curses

from display import AsyncDisplay


def pre_process(async_display: AsyncDisplay):
    async_display.stdscr.addstr(
        async_display.navigator[0],
        async_display.navigator[1],
        f"x={async_display.navigator[1]}/{async_display.navigator.limits[1][1]}, y={async_display.navigator[0]}/{async_display.navigator.limits[1][0]}",
        curses.color_pair(1),
    )


def program_end(async_display: AsyncDisplay):
    async_display.ok = False


async def __main__(stdscr):
    async_display = AsyncDisplay(stdscr)

    async_display.event(ord("\n"), program_end)

    await async_display.loop(pre=pre_process)


def main(stdscr) -> None:
    return asyncio.run(__main__(stdscr))


if __name__ == "__main__":
    curses.wrapper(main)
