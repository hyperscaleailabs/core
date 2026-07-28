"""SSH transport with a narrow, testable command boundary."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Protocol

from .config import Target


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str


class Transport(Protocol):
    def run(self, target: Target, command: str) -> Result:
        """Run a command on a target."""


class SshTransport:
    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def run(self, target: Target, command: str) -> Result:
        process = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                f"ConnectTimeout={self.timeout}",
                "-p",
                str(target.ssh_port),
                target.destination,
                command,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout + 5,
        )
        return Result(process.returncode, process.stdout, process.stderr)
