from __future__ import annotations

import time
from dataclasses import dataclass
from itertools import cycle
from subprocess import CompletedProcess

import click


def _spinner(chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
    """A spinner for showing progress."""
    frames = cycle(chars)
    while True:
        yield next(frames)


def _timer():
    """A timer which shows total time elapsed on each iteration."""
    start = time.monotonic()
    while True:
        yield f"{time.monotonic() - start:.1f}s"


@dataclass(frozen=True)
class Style:
    BOLD: str = "\033[1m"
    RESET: str = "\033[0m"


@dataclass(frozen=True)
class Color:
    RED: str = "\033[31m"
    GREEN: str = "\033[32m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    MAGENTA: str = "\033[35m"
    CYAN: str = "\033[36m"
    WHITE: str = "\033[37m"
    BLACK: str = "\033[30m"


@dataclass(frozen=True)
class BoldColor:
    RED: str = "\033[1;31m"
    GREEN: str = "\033[1;32m"
    YELLOW: str = "\033[1;33m"
    BLUE: str = "\033[1;34m"
    MAGENTA: str = "\033[1;35m"
    CYAN: str = "\033[1;36m"
    WHITE: str = "\033[1;37m"
    BLACK: str = "\033[1;30m"


class Spinner:
    def __init__(self, name: str, description: str | None = None, fps: float = 0.05):
        self.name = name
        self.description = f": {description}" if description else ""
        self.fps = fps
        self._timer = _timer()
        self._spinner = _spinner()
        self._last_timer_msg = ""

    def __call__(self):
        self._last_timer_msg = (
            f"\r {BoldColor.BLUE}{next(self._spinner)} {self.name}{Style.RESET}{Color.BLUE} ({next(self._timer)})"
            f"{self.description}{Style.RESET}"
        )
        click.echo(self._last_timer_msg, nl=False)
        time.sleep(self.fps)

    def _result_msg(self, color: str) -> str:
        return (
            f" {Style.BOLD}{self.name}{Style.RESET}{color} ({next(self._timer)})" f"{self.description}{Style.RESET}"
        ).ljust(len(self._last_timer_msg), " ")

    def _print_failure(self, result: CompletedProcess):
        output = "\n".join(stream.decode() for stream in [result.stdout, result.stderr] if stream)
        msg = f"{self._result_msg(Color.RED)}\n\n{output}" if output else self._result_msg
        click.secho(f"\r {Color.RED}✘{msg}")

    def _print_success(self):
        click.secho(f"\r {Color.GREEN}✔{self._result_msg(Color.GREEN)}")

    def print_results(self, result: CompletedProcess, error_msg_match: str = "", error_cls: type = click.Abort):
        """Prints the result of a command run.

        The command must be run with `stdout=PIPE` and `stderr=PIPE` to capture the output
        and show it after the command has finished.

        Args:
            result: The result of the command.
            error_msg_match: A string to match against the stdout and stderr. If any of the
                streams contains this string, the command is considered to have failed.
            error_cls: The error to raise if the command failed.
        """
        if result.returncode > 0 or (
            error_msg_match and (error_msg_match in result.stdout.decode() or error_msg_match in result.stderr.decode())
        ):
            self._print_failure(result)
            raise error_cls()

        self._print_success()
