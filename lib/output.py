import sys
import termios
from contextlib import contextmanager

from yaspin import Spinner, yaspin

FRAMES = Spinner(frames=["[\\]:", "[|]:", "[/]:", "[-]:"], interval=100)


def status(message):
    for line in str(message).splitlines() or [""]:
        print(f"[*]: {line}", file=sys.stderr)


@contextmanager
def spinner(text):
    if not sys.stderr.isatty():
        status(text)
        yield
        return
    with yaspin(FRAMES, text=text, stream=sys.stderr) as sp:
        yield
        sp.ok("[*]:")


@contextmanager
def hide_interrupt_echo():
    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
    except (ValueError, OSError, termios.error):
        yield
        return
    try:
        new = termios.tcgetattr(fd)
        new[3] &= ~termios.ECHOCTL
        termios.tcsetattr(fd, termios.TCSANOW, new)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)
