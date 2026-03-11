import shutil
from pathlib import Path

from ravyn import Ravyn
from tests.cli.utils import run_cmd

app = Ravyn(routes=[])


FOUND_DIRECTIVES = ["createapp", "createdeployment", "createproject", "runserver", "show_urls"]


def _set_test_settings(monkeypatch):
    monkeypatch.setenv("RAVYN_SETTINGS_MODULE", "tests.settings.AppTestSettings")


def test_list_directives_no_app(cli_tmp_dir: Path, monkeypatch):
    _set_test_settings(monkeypatch)
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn directives", is_app=False)
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)


def test_list_directives_with_app(cli_tmp_dir: Path, monkeypatch):
    _set_test_settings(monkeypatch)
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn directives")
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)


def test_list_directives_with_flag(cli_tmp_dir: Path, monkeypatch):
    _set_test_settings(monkeypatch)
    source_file = Path(__file__).resolve().parents[1] / "createsuperuser.py"
    run_cmd("tests.cli.main:app", "ravyn createproject myproject")

    directives_dir = cli_tmp_dir / "myproject/myproject/apps/myapp/directives/operations"
    directives_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(
        str(source_file),
        str(directives_dir / "createsuperuser.py"),
    )

    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn --app tests.cli.main:app directives")
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)

    assert "createsuperuser" in str(o)
