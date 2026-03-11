import os
import shlex
import shutil
from pathlib import Path


def _run_cmd(safe_run_cmd, cmd: str, is_app: bool = True, **kwargs):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = "tests.cli.main:app"
    process = safe_run_cmd(shlex.split(cmd), **kwargs)
    return process.stdout, process.stderr, process.returncode


def generate(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject")
    assert ss == 0

    apps_dir = cli_tmp_dir / "myproject/myproject/apps"
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createapp myapp", cwd=apps_dir)


def test_custom_directive(cli_tmp_dir: Path, safe_run_cmd):
    generate(cli_tmp_dir, safe_run_cmd)

    # Copy the createuser custom directive
    shutil.copyfile(
        Path(__file__).with_name("createusercli.py"),
        cli_tmp_dir / "myproject/myproject/apps/myapp/directives/operations/createusercli.py",
    )

    # Execute custom directive
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn")

    assert "create-user" in str(o)
    assert "Custom directive" in str(o)
