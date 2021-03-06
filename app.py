import asyncio
import curses
import math
import sys
from datetime import datetime


KEY = {'ESC': 27}


class Config:
    # Time intervals in seconds
    INTERVAL_WORK = 3
    INTERVAL_BREAK = 1
    # INTERVAL_WORK = 60 * 60  # 1 hour
    # INTERVAL_BREAK = 5 * 60  # 5 minutes
    N_BEEPS = 3


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

    # Do this instead of decorators, so that subclasses get this automatically
    show = asyncio.coroutine(show)

    def process_input(self):
        '''
        Handle user input key by running corresponding function
        '''
        key = self.w.getch()
        if key in {KEY['ESC'], ord('q'), ord('Q')}:
            self.stop()
            self.am.stop()

    def run(self):
        '''
        Show this widget and set up keyboard listener
        '''
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
        self.show_task.cancel()
        self.loop.remove_reader(sys.stdin)


class Options(Widget):

    HEIGHT = 10
    WIDTH = 46

    def process_input(self):
        key = self.w.getch()
        if key in {ord('b'), ord('B')}:
            self.am.register_intent(MainMenu)
            self.stop()
        elif key in {KEY['ESC'], ord('q'), ord('Q')}:
            self.stop()
            self.am.stop()
        elif key in {ord('W'), ord('w')}:
            curses.curs_set(True)
            curses.echo()
            self.am.config.INTERVAL_WORK = int(self.w.getstr(4, 31))
            curses.curs_set(False)
            curses.noecho()
        elif key in {ord('E'), ord('e')}:
            curses.curs_set(True)
            curses.echo()
            self.am.config.INTERVAL_BREAK = int(self.w.getstr(5, 35))
            curses.curs_set(False)
            curses.noecho()
        elif key in {ord('A'), ord('a')}:
            curses.curs_set(True)
            curses.echo()
            self.am.config.N_BEEPS = int(self.w.getstr(6, 23))
            curses.curs_set(False)
            curses.noecho()

    def show(self):
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        self.w.keypad(True)
        self.w.border(0)

        # Add welcome message at the top
        header = "Options"
        self.w.addstr(0, self.WIDTH // 2 - len(header) // 2, header)
        h2_txt = "To edit, press the key in ():"
        work_opt_txt = "(W) Work interval (seconds): {}"
        exer_opt_txt = "(E) Exercise interval (seconds): {}"
        beep_opt_txt = "(A) Number of beeps: {}"
        self.w.addstr(2, 2, h2_txt)
        self.w.addstr(4, 2, work_opt_txt.format(self.am.config.INTERVAL_WORK))
        self.w.addstr(5, 2, exer_opt_txt.format(self.am.config.INTERVAL_BREAK))
        self.w.addstr(6, 2, beep_opt_txt.format(self.am.config.N_BEEPS))
        self.w.addstr(8, 2, "B - Back to Main Menu  Q - Exit Program")
        while True:
            self.w.refresh()
            yield from asyncio.sleep(0.2)


class Timer(Widget):

    HEIGHT = 10
    WIDTH = 46

    def process_input(self):
        key = self.w.getch()
        if key in {ord('b'), ord('B')}:
            self.am.register_intent(MainMenu)
            self.stop()
        elif key in {KEY['ESC'], ord('q'), ord('Q')}:
            self.stop()
            self.am.stop()

    def show(self):
        time_start = datetime.now()
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        self.w.keypad(True)
        self.w.border(0)

        # Add welcome message at the top
        header = "Timer"
        self.w.addstr(0, self.WIDTH // 2 - len(header) // 2, header)
        self.w.addstr(2, 2, "Time remaining until break:")
        self.w.addstr(8, 2, "B - Back to Main Menu  Q - Exit Program")
        while True:
            time_diff = (datetime.now() - time_start).total_seconds()
            time_remain = self.am.config.INTERVAL_WORK - time_diff
            # Take a break when time runs out
            if time_remain <= 0:
                self.w.addstr(
                    4, 12, "{:2d} Minutes  {:2d} Seconds".format(0, 0))
                self.w.refresh()

                # Notify user it's breaktime
                for _ in range(self.am.config.N_BEEPS):
                    curses.flash()
                    curses.beep()
                    yield from asyncio.sleep(1)

                # Take a break (account for the flash/beep time above)
                yield from asyncio.sleep(
                    self.am.config.INTERVAL_BREAK - self.am.config.N_BEEPS)

                # Reset clock
                time_start = datetime.now()
                continue

            remaining_min, remaining_sec = divmod(time_remain, 60)
            # Countdown
            self.w.addstr(4, 12, "{:2d} Minutes  {:2d} Seconds".format(
                int(remaining_min), math.ceil(remaining_sec)))
            self.w.refresh()
            yield from asyncio.sleep(0.2)


class MainMenu(Widget):

    HEIGHT = 10
    WIDTH = 46

    def process_input(self):
        key = self.w.getch()
        if key in {KEY['ESC'], ord('q'), ord('Q')}:
            self.stop()
            self.am.stop()
        elif key in {ord('s'), ord('S')}:
            self.am.register_intent(Timer)
            self.stop()
        elif key in {ord('o'), ord('O')}:
            self.am.register_intent(Options)
            self.stop()

    def show(self):
        BEGIN_Y = (curses.LINES - 1) // 2 - self.HEIGHT // 2
        BEGIN_X = (curses.COLS - 1) // 2 - self.WIDTH // 2
        self.w = curses.newwin(self.HEIGHT, self.WIDTH, BEGIN_Y, BEGIN_X)
        self.w.keypad(True)
        # Window border
        self.w.border(0)

        # Add welcome message at the top
        header = "Take a break, go exercise!"
        self.w.addstr(0, self.WIDTH // 2 - len(header) // 2, header)
        self.w.addstr(2, 2, "Select from one of the following options:")
        self.w.addstr(4, 4, "S - Start Timer")
        self.w.addstr(5, 4, "O - Options")
        self.w.addstr(6, 4, "Q - Exit Program")
        while True:
            self.w.addstr(
                8, 2, datetime.now().strftime("%A %B %d, %Y  %I:%M:%S%p"))
            self.w.refresh()
            yield from asyncio.sleep(0.2)


class AppManager:
    def __init__(self, config):
        self.config = config
        self.loop = None
        self.main_task = None
        self.intents = asyncio.Queue(maxsize=1)
        self.intents.put_nowait(MainMenu)

    def main(self):
        while True:
            widget_class = yield from self.intents.get()
            yield from widget_class(self).run()
    main = asyncio.coroutine(main)

    def run(self, stdscr):
        # Invisible cursor
        try:
            curses.curs_set(False)
        except:
            # Ugly hack for no TERM support
            pass

        self.loop = asyncio.get_event_loop()
        self.main_task = asyncio.async(self.main())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def register_intent(self, widget_class):
        '''
        Register next widget to show
        '''
        self.intents.put_nowait(widget_class)

    def stop(self):
        '''
        Stop the main loop
        '''
        self.main_task.cancel()
        self.loop._run_once()
        self.loop.stop()


if __name__ == "__main__":
    try:
        am = AppManager(Config())
        curses.wrapper(am.run)
    except KeyboardInterrupt:
        sys.stderr.write("Ctrl-c exit\n\n")
        sys.exit(1)
