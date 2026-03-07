import os
import sys
from pathlib import Path
from typing import Annotated, Any, cast

import click
from lilya.types import ASGIApp
from rich.tree import Tree
from sayer import Argument, Option, command, error

from ravyn.core.directives.env import DirectiveEnv
from ravyn.core.directives.exceptions import DirectiveError
from ravyn.core.terminal.utils import get_log_config, get_ui_toolkit


def get_app_tree(module_paths: list[Path], discovery_file: str) -> Tree:
    """
    Generates a tree structure representing the application modules.
    """
    root = module_paths[0]
    name = f"{root.name}" if root.is_file() else f"📁 {root.name}"

    root_tree = Tree(name)

    if root.is_dir():
        init_path = root / "__init__.py"
        if init_path.is_file():
            root_tree.add("[dim]__init__.py[/dim]")
            root_tree.add(f"[dim]{discovery_file}[/dim]")

    tree = root_tree
    for sub_path in module_paths[1:]:
        sub_name = f"{sub_path.name}" if sub_path.is_file() else f"📁 {sub_path.name}"
        tree = tree.add(sub_name)
        if sub_path.is_dir():
            tree.add("[dim]__init__.py[/dim]")
            tree.add(f"[dim]{discovery_file}[/dim]")

    return root_tree


@command
def runserver(
    path: Annotated[str | None, Argument(help="Path to the application.", required=False)],
    *,
    port: Annotated[
        int, Option(8000, "-p", help="Port to run the development server.", show_default=True)
    ],
    reload: Annotated[
        bool, Option(False, "-r", help="Reload server on file changes.", show_default=True)
    ],
    host: Annotated[
        str, Option(default="localhost", help="Host to run the server on.", show_default=True)
    ],
    debug: Annotated[
        bool, Option(default=True, help="Run the server in debug mode.", show_default=True)
    ],
    log_level: Annotated[
        str, Option(default="debug", help="Log level for the server.", show_default=True)
    ],
    lifespan: Annotated[
        str, Option(default="on", help="Enable lifespan events.", show_default=True)
    ],
    settings: Annotated[
        str | None,
        Option(help="Any custom settings to be initialised.", required=False, show_default=False),
    ],
    proxy_headers: Annotated[
        bool,
        Option(
            default=True,
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info.",
            show_default=True,
        ),
    ],
    workers: Annotated[
        int | None,
        Option(
            default=None,
            help="Use multiple worker processes. Mutually exclusive with the --reload flag.",
            required=False,
        ),
    ],
) -> None:
    """Starts the Ravyn development server.

    The --app can be passed in the form of <module>.<submodule>:<app> or be set
    as environment variable RAVYN_DEFAULT_APP.

    Alternatively, if none is passed, Ravyn will perform the application discovery.

    It is strongly advised not to run this command in any other environment but development.
    This was designed to facilitate the development environment and should not be used in production.

    How to run: `ravyn runserver`
    """
    ctx = click.get_current_context()
    env = ctx.ensure_object(DirectiveEnv)
    with get_ui_toolkit() as toolkit:
        # Analyse the app structure
        toolkit.print(
            "[gray50]Identifying package structures based on directories with [green]__init__.py[/green] files[/gray50]"
        )

        if getattr(env, "app", None) is None:
            error(
                "You cannot specify a custom directive without specifying the --app or setting "
                "RAVYN_DEFAULT_APP environment variable."
            )
            sys.exit(1)

        if settings is not None:
            os.environ.setdefault("RAVYN_SETTINGS_MODULE", settings)

        try:
            import palfrey
        except ImportError:
            raise DirectiveError(
                detail="Palfrey needs to be installed to run Ravyn. Run `pip install palfrey`."
            ) from None

        server_environment: str = ""
        if os.environ.get("RAVYN_SETTINGS_MODULE"):
            from ravyn.conf import settings as ravyn_settings

            environment = getattr(ravyn_settings, "environment", "development")
            server_environment = f"{environment}"

        if not server_environment:
            server_environment = "development"

        toolkit.print_title(f"[green]Starting {server_environment} server[/green]", tag="Ravyn")
        toolkit.print(f"Importing from [green]{env.command_path}[/green]", tag="Ravyn")
        toolkit.print(f"Importing module '{env.path}'", tag="Ravyn")
        toolkit.print_line()

        module_info = env.module_info
        if (
            module_info
            and module_info.module_paths
            and module_info.discovery_file
            and module_info.module_import
        ):
            root_tree = get_app_tree(
                module_info.module_paths, discovery_file=module_info.discovery_file
            )
            toolkit.print(root_tree, tag="module")
            toolkit.print_line()
            toolkit.print(
                "The [bold]Ravyn[/bold] object is imported using the following code:",
                tag="code",
            )
            toolkit.print(
                f"[underline]from [bold]{module_info.module_import[0]}[/bold] import [bold]{module_info.module_import[1]}[/bold]",
                tag=module_info.module_import[1],
            )

        url = f"http://{host}:{port}"
        docs = f"http://{host}:{port}/docs/swagger"
        toolkit.print_line()
        toolkit.print(
            f"Server started at [link={url}]{url}[/]",
            tag="server",
        )
        toolkit.print(
            f"Visit the docs at [link={docs}]{docs}[/]",
            tag="docs",
        )

        if os.environ.get("RAVYN_SETTINGS_MODULE"):
            custom_message = f"'{os.environ.get('RAVYN_SETTINGS_MODULE')}'"
            toolkit.print(
                f"Using custom settings module: [bold][green]{custom_message}[/green][/bold]",
                tag="settings",
            )
        else:
            from ravyn.conf import settings as ravyn_settings

            toolkit.print(
                f"Using default settings module: [bold][green]{ravyn_settings.__class__.__module__}.Settings[/green][/bold]",
                tag="settings",
            )

        toolkit.print_line()
        toolkit.print(
            "[green]You can use the runserver to run in production too.[/green]",
            tag="note",
        )

        if debug and env.ravyn_app:
            env.ravyn_app.debug = debug  # type: ignore[attr-defined]

        toolkit.print_line()

        # Determine which app path or object to run
        app_target: str | ASGIApp
        if path:
            # User explicitly provided the app path (e.g., myproject.main:app)
            app_target = path
            toolkit.print(f"Using app path provided: [green]{path}[/green]", tag="Ravyn")
        elif env.path:
            # Use discovered or environment app path
            app_target = env.path
        else:
            error(
                "No application path found. Provide it via CLI or environment variable 'RAVYN_DEFAULT_APP'."
            )
            sys.exit(1)

        if not reload and not workers:
            # Run using the actual loaded app instance when possible
            app_to_run = env.app or app_target
        else:
            # Use import path string for reload/workers compatibility
            app_to_run = app_target

        palfrey.run(  # type: ignore[call-overload]
            # in case of no reload and workers, we might end up initializing twice when
            # using a function, so use app instead
            config_or_app=app_to_run,
            port=port,
            host=host,
            reload=reload,
            lifespan=cast(Any, lifespan),
            log_level=log_level,
            proxy_headers=proxy_headers,
            workers=workers,
            log_config=get_log_config(),
        )
