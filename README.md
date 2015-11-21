# brexerise

This application reminds you to take a break from coding or working at a desk every hour or so and do some exercises and stretching.

I wrote this app mainly to learn about Python's asyncio library. It uses the curses library to display text-based UI in the terminal.

Python 3.4 is required to run in Mac OSX and Linux systems.
(I haven't tested it in Windows, and it probably won't work)

To run, open terminal and enter the following command:
```
python app.py
```
Or if your default Python version is 2.x:
```
python3 app.py
```

The UI is broken for 'ansi' terminals.
To check your terminal settings:
```
echo $TERM
```
