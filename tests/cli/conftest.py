import subprocess
from pathlib import Path

import pytest  # type: ignore[import-not-found]
from sayer.testing import SayerTestClient  # type: ignore[import-not-found]

from ravyn.core.directives.cli import ravyn_cli


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": True})


@pytest.fixture
def cli_tmp_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide isolated temporary cwd for CLI tests.

    Uses pytest's ``tmp_path`` and ``monkeypatch.chdir`` so each test runs in a
    clean directory and the original cwd is restored automatically after test
    teardown.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def safe_run_cmd(cli_tmp_dir: Path):
    """Run subprocess commands safely without ``shell=True``.

    Accepts command as argument list (e.g. ``["ravyn", "createproject", "app"]``)
    and returns ``subprocess.CompletedProcess`` with captured output for asserts.
    ``cli_tmp_dir`` is injected to ensure execution happens in an isolated cwd.
    """

    def _run(cmd: list[str], **kwargs):
        return subprocess.run(cmd, capture_output=True, text=True, shell=False, **kwargs)

    return _run


@pytest.fixture
def cli_project_scaffold(cli_tmp_dir: Path) -> Path:
    """Create a minimal Ravyn project skeleton in the isolated test directory.

    This scaffold is intentionally small and reusable for CLI tests that need a
    project-like layout without creating artifacts in the repository root.
    """
    project_dir = cli_tmp_dir / "test_project"
    package_dir = project_dir / "test_project"
    package_dir.mkdir(parents=True)

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_project"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / "README.md").write_text("# test_project\n", encoding="utf-8")
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "main.py").write_text("app = None\n", encoding="utf-8")

    return project_dir


@pytest.fixture
def client():
    """Fixture to provide a test client for the Lilya CLI."""
    return SayerTestClient(ravyn_cli)
