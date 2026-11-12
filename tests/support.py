"""Shared plumbing for the test modules.

Importing this module puts every skills/*/scripts directory on sys.path and refuses to load when two scripts
share a module name, since one process holds them all. It also holds:

    never_run(*allowed)    in setUpModule: subprocess.run and subprocess.Popen refuse any command whose
                           argv[0] (or its basename) is not listed, and git sees no global or system config
    limit_starts_when(method, ready)
                           a production limit counts from the command's start; hold it until `ready()` so a
                           slow start on a loaded machine cannot spend it before the command is up
    temp_git_repo(path)    a git repository with a fixed identity, shut out from the user's git config
    git(repo, *args)       run git in a repository under the same isolation
    run_main(main, argv)   run a CLI main(argv) and return (exit code, stdout, stderr)
    run_in_locale(locale, code, *args)
                           run Python code in a child under LC_ALL=locale with UTF-8 mode off, so a locale the
                           host lacks leaves the child in an ASCII locale instead of UTF-8 mode; returns bytes
    Recorder, reply, fixture, adapter
                           the injected runner and recorded replies of the backend adapter tests
"""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import time
import unittest
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ADW = ROOT / "skills" / "agent-delivery-workflow"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def insert_script_dirs(root: Path) -> None:
    owners: dict[str, Path] = {}
    for scripts in sorted(root.glob("skills/*/scripts")):
        for entry in sorted(scripts.iterdir()):
            if entry.suffix == ".py":
                name = entry.stem
            elif (entry / "__init__.py").is_file():
                name = entry.name
            else:
                continue
            if name in owners:
                raise ImportError(f"script module {name} is in both {owners[name]} and {scripts}")
            owners[name] = scripts
        sys.path.insert(0, str(scripts))


insert_script_dirs(ROOT)

_REAL_RUN = subprocess.run
_REAL_POPEN = subprocess.Popen

GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}
GIT_ISOLATION = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def _guard(real: Callable[..., Any], allowed: Sequence[str]) -> Callable[..., Any]:
    def guarded(args: Any, *rest: Any, **kwargs: Any) -> Any:
        first = args if isinstance(args, (str, bytes, os.PathLike)) else args[0]
        command = os.fsdecode(first)
        if command not in allowed and os.path.basename(command) not in allowed:
            raise AssertionError(f"tests run only {tuple(allowed)}, not {command}")
        return real(args, *rest, **kwargs)

    return guarded


@contextlib.contextmanager
def guarded(*allowed: str) -> Iterator[None]:
    with mock.patch.object(subprocess, "run", new=_guard(_REAL_RUN, allowed)), \
            mock.patch.object(subprocess, "Popen", new=_guard(_REAL_POPEN, allowed)), \
            mock.patch.dict(os.environ, {**GIT_IDENTITY, **GIT_ISOLATION}):
        yield


@contextlib.contextmanager
def limit_starts_when(method: str, ready: Callable[[], object]) -> Iterator[None]:
    """Make the production limit of Popen.`method` ("wait" or "communicate") count from when `ready()` holds.

    A call that carries a timeout first waits, up to 60s, for `ready()`; the timeout then runs as written.
    """
    real = getattr(_REAL_POPEN, method)

    def held(self: subprocess.Popen, *args: Any, timeout: float | None = None, **kwargs: Any) -> Any:
        if timeout is not None:
            deadline = time.monotonic() + 60
            while not ready():
                if time.monotonic() > deadline:
                    raise AssertionError(f"the command was not up within 60s of its start (Popen.{method})")
                time.sleep(0.02)
        return real(self, *args, timeout=timeout, **kwargs)

    with mock.patch.object(_REAL_POPEN, method, held):
        yield


def never_run(*allowed: str) -> None:
    """Call from setUpModule; unittest's module cleanup undoes it."""
    stack = contextlib.ExitStack()
    stack.enter_context(guarded(*allowed))
    unittest.addModuleCleanup(stack.close)


def git(repo: Path, *args: str) -> str:
    return _REAL_RUN(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        stdin=subprocess.DEVNULL,
        env={**os.environ, **GIT_IDENTITY, **GIT_ISOLATION},
    ).stdout.strip()


def temp_git_repo(path: Path, *, bare: bool = False) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main", *(["--bare"] if bare else []))
    if bare:
        return path
    git(path, "config", "user.name", GIT_IDENTITY["GIT_AUTHOR_NAME"])
    git(path, "config", "user.email", GIT_IDENTITY["GIT_AUTHOR_EMAIL"])
    return path


def run_main(
    main: Callable[[list[str]], int | None], argv: list[str], stdin: str | None = None
) -> tuple[int | None, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), contextlib.ExitStack() as stack:
        if stdin is not None:
            stack.enter_context(mock.patch.object(sys, "stdin", io.StringIO(stdin)))
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def run_in_locale(locale: str, code: str, *args: str) -> subprocess.CompletedProcess[bytes]:
    inherited = {key: value for key, value in os.environ.items() if key != "PYTHONIOENCODING"}
    return subprocess.run(
        [sys.executable, "-c", code, *args],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        env={**inherited, "LC_ALL": locale, "PYTHONUTF8": "0"},
    )


def fixture(backend_name: str, name: str) -> str:
    return (FIXTURES / "backends" / backend_name / name).read_text(encoding="utf-8")


def reply(tool: str, stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([tool], returncode, stdout, stderr)


class Recorder:
    """The runner injected into an adapter: records (args, timeout) in `calls`, env in `envs`, and answers the queued replies in order."""

    def __init__(self, *replies: subprocess.CompletedProcess[str]) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[list[str], float]] = []
        self.envs: list[dict[str, str] | None] = []

    def __call__(
        self, args: list[str], *, timeout: float = 30.0, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        self.calls.append((list(args), timeout))
        self.envs.append(env)
        return self.replies.pop(0)

    @property
    def argv(self) -> list[list[str]]:
        return [args for args, _ in self.calls]


def adapter(
    module: Any, environ: dict[str, str], *replies: subprocess.CompletedProcess[str], **options: Any
) -> tuple[Any, Recorder]:
    runner = Recorder(*replies)
    return module.Adapter(environ, runner=runner, **options), runner
