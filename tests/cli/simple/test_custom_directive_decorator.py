import os
import shlex
import shutil
from pathlib import Path

import pytest  # type: ignore

from tests.cli.user import User, models

pytestmark = pytest.mark.anyio


def _run_cmd(safe_run_cmd, cmd: str, is_app: bool = True, **kwargs):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = "tests.cli.main:app"
    process = safe_run_cmd(shlex.split(cmd), **kwargs)
    return process.stdout, process.stderr, process.returncode


@pytest.fixture(autouse=True, scope="function")
async def create_test_database():
    try:
        with models.database.force_rollback(False):
            async with models:
                await models.create_all()
                yield
                await models.drop_all()
    except Exception:
        pytest.skip("No database available")


def generate(cli_tmp_dir: Path, safe_run_cmd):
    (o, e, ss) = _run_cmd(safe_run_cmd, "ravyn createproject myproject --simple")
    assert ss == 0


async def test_custom_directive(cli_tmp_dir: Path, safe_run_cmd):
    generate(cli_tmp_dir, safe_run_cmd)
    assert models.models["User"] is User

    users = await User.query.all()

    assert len(users) == 0

    operations_dir = cli_tmp_dir / "myproject/myproject/apps/myapp/directives/operations"
    operations_dir.mkdir(parents=True)

    # Copy the createuser custom directive
    shutil.copyfile(
        Path(__file__).resolve().parents[1] / "createuser.py",
        operations_dir / "createuser.py",
    )

    # Execute custom directive
    name = "Ravyn"
    (o, e, ss) = _run_cmd(safe_run_cmd, f"ravyn run createuser -n {name}")

    users = await User.query.all()

    assert len(users) == 1

    user = await User.query.get(first_name=name)

    assert user.first_name == name
    assert user.email == "mail@ravyn.dev"
    assert user.is_superuser is True
