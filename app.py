import asyncio
import curses
import sys
from datetime import datetime


class Widget:

    def __init__(self, key_action):
        '''
        Initialize user input keys to actions
        key_actions is a dictionary mapping characters to functions
        '''
        self.key_action = key_action

    def show(self):
        '''
        Must implement this method to display window
        '''
        raise NotImplementedError("Method not implemented")
    show = asyncio.coroutine(show)

    def process_input(self):
        '''
        Handle user input key by running corresponding function
        '''
        key = self.w.getch()
        if key in self.key_action:
            self.key_action[key]()

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            # Add listener for user keyboard input
            loop.add_reader(sys.stdin, self.process_input)
            loop.run_until_complete(self.show())
        finally:
            loop.close()


class Timer(Widget):

    HEIGHT = 10
    WIDTH = 46

    def show(self):
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        self.w.border(0)

        # Add welcome message at the top
        top_message = "Running Timer"
        self.w.addstr(
            0, self.WIDTH // 2 - len(top_message) // 2, top_message)
        self.w.addstr(2, 2, "Select from one of the following options:")
        self.w.addstr(4, 4, "S - Start Timer")
        self.w.addstr(5, 4, "Q - Exit Program")
        while True:
            self.w.addstr(
                8, 2, datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
            self.w.refresh()
            yield from asyncio.sleep(0.2)


class MainMenu(Widget):

    HEIGHT = 10
    WIDTH = 46

    def show(self):
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        # Window border
        self.w.border(0)

        # Add welcome message at the top
        top_message = "Welcome to Brexercise (Break and Exercise)!"
        self.w.addstr(
            0, self.WIDTH // 2 - len(top_message) // 2, top_message)
        self.w.addstr(2, 2, "Select from one of the following options:")
        self.w.addstr(4, 4, "S - Start Timer")
        self.w.addstr(5, 4, "Q - Exit Program")
        while True:
            self.w.addstr(
                8, 2, datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
            self.w.refresh()
            yield from asyncio.sleep(0.2)


class App:
    def run(self, stdscr):
        # Invisible cursor
        curses.curs_set(0)

        # Show main menu
        MainMenu({
            27: lambda: sys.exit(1),
            ord('q'): lambda: sys.exit(1),
            ord('Q'): lambda: sys.exit(1)}).run()


if __name__ == "__main__":
    try:
        curses.wrapper(App().run)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
