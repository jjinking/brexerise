import asyncio
import curses
import logging
import sys
from datetime import datetime
from queue import Queue

logging.basicConfig(filename='app2.log', level=logging.DEBUG)

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
        logging.info("Starting Widget.run")
        self.loop = asyncio.get_event_loop()
        # Add listener for user keyboard input
        self.loop.add_reader(sys.stdin, self.process_input)

        # Show this widget
        self.show_task = asyncio.async(self.show())
        yield

    def stop(self):
        '''
        Stop showing this widget
        '''
        logging.info("Stopping widget show task")
        self.show_task.cancel()
        self.loop.remove_reader(sys.stdin)
        logging.info("Finished stopping widget")


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
        logging.info("Starting Timer.show")
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
            self.loop.stop()
            # self.loop.close()
        elif key in {ord('s'), ord('S')}:
            self.am.register_intent(Timer)
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
    def __init__(self):
        self.intents = asyncio.Queue(maxsize=1)
        self.intents.put_nowait(MainMenu)

    def main(self):
        logging.info("Started AppManager.main")
        while True:
            widget_class = yield from self.intents.get()
            logging.info("Acquired {} from intents".format(widget_class))
            yield from widget_class(self).run()
            logging.info("Finished running {}".format(str(widget_class)))
        logging.info("Finished AppManager.main")
    main = asyncio.coroutine(main)

    def run(self, stdscr):
        logging.info("Starting AppManager.run")

        # Invisible cursor
        curses.curs_set(0)

        loop = asyncio.get_event_loop()
        asyncio.async(self.main())
        loop.run_forever()
        logging.info("Finished AppManager.run")

    def register_intent(self, widget_class):
        '''
        Register next widget to show
        '''
        logging.info("Registering new widget {}".format(str(widget_class)))
        self.intents.put_nowait(widget_class)


if __name__ == "__main__":
    try:
        curses.wrapper(AppManager().run)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
