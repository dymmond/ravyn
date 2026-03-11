import os
import shlex
import shutil
from pathlib import Path

from ravyn import Ravyn

app = Ravyn(routes=[])


FOUND_DIRECTIVES = ["createapp", "createproject", "runserver", "show_urls"]


def _run_cmd(safe_run_cmd, cmd: str, is_app: bool = True, **kwargs):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = "tests.cli.main:app"
    process = safe_run_cmd(shlex.split(cmd), **kwargs)
    return process.stdout, process.stderr, process.returncode


def test_list_directives_no_app(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn directives", is_app=False)
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)


def test_list_directives_with_app(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn directives")
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)


def test_list_directives_with_flag(cli_tmp_dir: Path, safe_run_cmd):
    _run_cmd(safe_run_cmd, "ravyn createproject myproject")

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createapp myapp", cwd=apps_dir)

    shutil.copyfile(
        Path(__file__).with_name("createsuperuser.py"),
        cli_tmp_dir / "myproject/myproject/apps/myapp/directives/operations/createsuperuser.py",
    )

    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn --app tests.cli.main:app directives")
    assert ss == 0

    for directive in FOUND_DIRECTIVES:
        assert directive in str(o)

    assert "createsuperuser" in str(o)
