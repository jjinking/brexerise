import asyncio
import curses
import time
import sys
from datetime import datetime

KEYS_EXIT = {27, ord('q'), ord('Q')}


@asyncio.coroutine
def get_user_input(window):
    yield window.getchr()


@asyncio.coroutine
def listen(window):
    while True:
        yield from get_user_input()
        if key in self.KEYS_EXIT:
            break


@asyncio.coroutine
def main_menu():
    # Set up window
    height = 10
    width = 46
    begin_y = (curses.LINES - 1) // 2 - height // 2
    begin_x = (curses.COLS - 1) // 2 - width // 2
    window = curses.newwin(height, width, begin_y, begin_x)
    window.border(0)

    # Add welcome message at the top
    top_message = "Welcome to Brexercise (Break and Exercise)!"
    window.addstr(0, width // 2 - len(top_message) // 2, top_message)
    window.addstr(2, 2, "Select from one of the following options:")
    window.addstr(4, 4, "S - Start Timer")
    window.addstr(5, 4, "Q - Exit Program")

    while True:
        yield from asyncio.sleep(0.2)
        window.addstr(
            8, 2, datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
        window.refresh()


def main(stdscr):
    main_menu()
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.async(main_menu()),
        # asyncio.ensure_future(listen()),
    ]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
