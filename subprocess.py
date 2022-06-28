import asyncio
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Iterator, Optional

from boost.core.errors import BoostExecutionError, BoostRuntimeError
from boost.core.globals import (
    BOOST_EXEC_DEFAULT_TIMEOUT,
    BOOST_EXEC_SUBPROCESS_BUFFER,
)

__all__ = [
    "execute",
    "output",
]


logger = logging.getLogger("boost.command")
output_logger = logging.getLogger("boost.command.stdout")
error_logger = logging.getLogger("boost.command.stderr")


class CompletedProcess:
    def __init__(
            self,
            command: str,
            args: tuple[str, ...],
            returncode: Optional[int] = 0,
            stdout: Optional[list[str]] = None,
            stderr: Optional[list[str]] = None,
    ) -> None:
        self.command = command
        self.args = args
        self.returncode = returncode
        self.stdout = stdout or []
        self.stderr = stderr or []


async def read_stream(
        stream: Optional[asyncio.StreamReader],
        callback: Callable[[str], Awaitable[None]],
        strip_with: Callable[[str], str],
) -> None:
    if not stream:
        return

    while True:
        line = await stream.readline()

        if not line:
            break

        line = str(line, "utf-8")

        if strip_with:
            line = strip_with(line)

        await callback(line)


async def write_stream(
        stream: Optional[asyncio.StreamWriter],
        values: Optional[Iterable[str]],
) -> None:
    if not stream or not values:
        return

    for line in values:
        stream.write(bytes(line, "utf-8"))
        await stream.drain()
    stream.close()


async def execute(
        command: str,
        *args: str,
        limit: int = BOOST_EXEC_SUBPROCESS_BUFFER,
        check: Optional[bool] = True,
        logger: logging.Logger = logger,
        error_logger: logging.Logger = error_logger,
        output_logger: logging.Logger = output_logger,
        strip_with: Callable[[str], str] = str.strip,
        stderr_cb: Optional[Callable[[str], Awaitable[None]]] = None,
        stdin_iter: Optional[Iterator[str]] = None,
        stdout_cb: Optional[Callable[[str], Awaitable[None]]] = None,
        timeout: Optional[int] = BOOST_EXEC_DEFAULT_TIMEOUT,
        verbose: Optional[bool] = None,
        **kwargs: Any,
) -> CompletedProcess:
    result = CompletedProcess(command, args, -1)

    if verbose is None:
        verbose = output_logger.level <= logging.DEBUG

    async def read_output(line: str) -> None:
        if verbose:
            if len(line) > 1024:
                output_logger.debug(line[0:1021] + "...")
            else:
                output_logger.debug(line)

        if stdout_cb:
            await stdout_cb(line)

    async def read_error(line: str) -> None:
        if verbose:
            if len(line) > 1024:
                error_logger.debug(line[0:1021] + "...")
            else:
                error_logger.debug(line)

        if stderr_cb:
            await stderr_cb(line)

    try:
        logger.debug(f"{command}, {' '.join(args)}")
        subprocess = await asyncio.create_subprocess_exec(
            command,
            *args,
            limit=limit,
            stdin=None if stdin_iter is None else asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            **kwargs,
        )

        await asyncio.wait_for(
            asyncio.gather(
                read_stream(subprocess.stdout, read_output, strip_with),
                read_stream(subprocess.stderr, read_error, strip_with),
                write_stream(subprocess.stdin, stdin_iter),
                subprocess.wait(),
            ),
            timeout=timeout,
        )

    except asyncio.exceptions.TimeoutError as e:
        try:
            subprocess.kill()
        except OSError:
            pass

        command = Path(command).name
        result.returncode = subprocess.returncode

        raise BoostRuntimeError(
            f"command '{command}' timed out after {timeout} seconds",
        ) from e

    except FileNotFoundError as e:
        result.returncode = 127
        result.stderr = [f"command '{command}' failed, executable not found"]

        raise BoostExecutionError(
            f"command '{command}' failed, executable not found",
            process=result,
        ) from e

    except ValueError as e:
        if str(e) == "Separator is found, but chunk is longer than limit":
            result.returncode = subprocess.returncode
            raise BoostExecutionError(
                f"command '{command}' output exceeded maximum buffer size",
                process=result,
            ) from e

    result.returncode = subprocess.returncode

    if check and result.returncode != 0:
        raise BoostExecutionError(
            f"command '{command} {args}' exited with non-zero ({result.returncode})"
            + " exit status",
            process=result,
            )

    return result


async def output(
        *args: str,
        combined: bool = False,
        **kwargs: Any,
) -> CompletedProcess:
    stdout: list[str] = []
    stderr: list[str] = stdout if combined else []

    async def collect_output(line: str) -> None:
        stdout.append(line)

    async def collect_stderr(line: str) -> None:
        stderr.append(line)

    try:
        result = await execute(
            *args, stderr_cb=collect_stderr, stdout_cb=collect_output, **kwargs
        )
        result.stderr = stderr
        result.stdout = stdout
    except BoostExecutionError as error:
        error.process.stderr = stderr if stderr else error.process.stderr
        error.process.stdout = stdout if stdout else error.process.stdout
        raise error

    return result
