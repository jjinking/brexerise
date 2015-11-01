import asyncio
import curses
import sys
from datetime import datetime

KEYS_EXIT = {27, ord('q'), ord('Q')}

HEIGHT = 10
WIDTH = 46


@asyncio.coroutine
def main_menu(window):
    # Set up window
    window.border(0)

    # Add welcome message at the top
    top_message = "Welcome to Brexercise (Break and Exercise)!"
    window.addstr(0, WIDTH // 2 - len(top_message) // 2, top_message)
    window.addstr(2, 2, "Select from one of the following options:")
    window.addstr(4, 4, "S - Start Timer")
    window.addstr(5, 4, "Q - Exit Program")
    while True:
        window.addstr(
            8, 2, datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
        window.refresh()
        yield from asyncio.sleep(0.2)


def process_input(window):
    """
    User input
    """
    key = window.getch()
    if key in KEYS_EXIT:
        sys.exit(1)


def main(stdscr):
    # Invisible cursor
    curses.curs_set(0)
    BEGIN_Y = (curses.LINES - 1) // 2 - HEIGHT // 2
    BEGIN_X = (curses.COLS - 1) // 2 - WIDTH // 2
    window = curses.newwin(HEIGHT, WIDTH, BEGIN_Y, BEGIN_X)
    window.nodelay(True)  # Nonblocking
    loop = asyncio.get_event_loop()
    try:
        # Add listener for user keyboard input
        loop.add_reader(sys.stdin, process_input, window)
        loop.run_until_complete(main_menu(window))
    finally:
        loop.close()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
