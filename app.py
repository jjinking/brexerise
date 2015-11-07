import asyncio
import curses
import sys
from datetime import datetime
from queue import Queue

ESC_KEY = 27


class Widget:

    def __init__(self, am):
        '''
        Register app manager with each widget
        '''
        self.am = am

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
            pass
            # self.loop.close()

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
            self.am.register_intent(Timer)

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
    def __init__(self):
        self.intents = Queue(1)
        self.intents.put(MainMenu)

    def run(self, stdscr):
        # Invisible cursor
        curses.curs_set(0)

        while not self.intents.empty():
            widget_class = self.intents.get()
            widget_class(self).run()

    def register_intent(self, widget_class):
        '''
        Register next widget to show
        '''
        self.intents.put(widget_class)


if __name__ == "__main__":
    try:
        curses.wrapper(AppManager().run)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
