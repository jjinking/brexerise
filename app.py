import asyncio
import curses
import sys
from datetime import datetime

ESC_KEY = 27


class Widget:

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
        if key in {ord('q'), ord('Q')}:
            self.stop()

    def run(self):
        '''
        Show this widget and set up keyboard listener
        '''
        self.loop = asyncio.get_event_loop()
        try:
            # Add listener for user keyboard input
            self.loop.add_reader(sys.stdin, self.process_input)

            # Show this widget
            self.show_task = asyncio.async(self.show())
            self.loop.run_forever()
        finally:
            self.loop.close()

    def stop(self):
        '''
        Stop showing this widget
        '''
        self.show_task.cancel()
        self.loop.remove_reader(sys.stdin)
        self.loop.stop()


class Timer(Widget):

    HEIGHT = 10
    WIDTH = 46

    def process_input(self):
        key = self.w.getch()
        if key == ESC_KEY:
            sys.exit(1)
        elif key in {ord('q'), ord('Q')}:
            sys.exit(1)

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

    def process_input(self):
        key = self.w.getch()
        if key in {ESC_KEY, ord('q'), ord('Q')}:
            self.stop()
        elif key in {ord('s'), ord('S')}:
            self.stop()

    def show(self):
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        # Window border
        self.w.border(0)

        # Add welcome message at the top
        top_message = "Take a break, go exercise!"
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


class AppManager:

    def run(self, stdscr):
        # Invisible cursor
        curses.curs_set(0)
        self.show_main_menu()

    def show_main_menu(self):
        MainMenu().run()

    def show_timer(self):
        Timer().run()


if __name__ == "__main__":
    try:
        curses.wrapper(AppManager().run)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
