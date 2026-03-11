import sys
from pathlib import Path

import pytest  # type: ignore[import-not-found]


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive(client, cli_tmp_dir: Path, monkeypatch: pytest.MonkeyPatch):
    # Create the project
    (cli_tmp_dir / "main.py").write_text(
        "from ravyn import Ravyn\n\napp = Ravyn(routes=[])\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RAVYN_DEFAULT_APP", "main:app")
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--subject",
            "Hello",
            "--text",
            "Plain message",
        ]
    )

    assert result.exit_code == 0
    assert "Test email sent to 'user@example.com' using console backend." in result.output


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive_to_multiple(
    client, cli_tmp_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    # Create the project
    (cli_tmp_dir / "main.py").write_text(
        "from ravyn import Ravyn\n\napp = Ravyn(routes=[])\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RAVYN_DEFAULT_APP", "main:app")
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--to",
            "user2@example.com",
            "--subject",
            "Hello",
            "--text",
            "Plain message",
        ]
    )

    assert result.exit_code == 0


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_send_mail_directive_html(client, cli_tmp_dir: Path, monkeypatch: pytest.MonkeyPatch):
    # Create the project
    (cli_tmp_dir / "main.py").write_text(
        "from ravyn import Ravyn\n\napp = Ravyn(routes=[])\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RAVYN_DEFAULT_APP", "main:app")
    result = client.invoke(["createproject", "myproject"])

    assert result.exit_code == 0

    # Run the sendtest mail directive
    result = client.invoke(
        [
            "mail",
            "sendtest",
            "--to",
            "user@example.com",
            "--subject",
            "Hello",
            "--html",
            "<h1>HTML message</h1>",
        ]
    )

    assert result.exit_code == 0
    assert "<h1>HTML message</h1>" in result.output
