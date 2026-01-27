from __future__ import annotations

from typing import Annotated

import click
from sayer import Argument, Option, command, error, success

from ravyn.core.directives.exceptions import DirectiveError
from ravyn.core.directives.operations._constants import SECRET_KEY_INSECURE_PREFIX
from ravyn.core.directives.templates import TemplateDirective
from ravyn.utils.crypto import get_random_secret_key


@command(name="createapp")
def create_app(
    names: Annotated[
        list[str],
        Argument(
            nargs=-1,
            type=click.UNPROCESSED,
            help="The name of the app or list of apps to create.",
        ),
    ],
    verbosity: Annotated[int, Option(1, "-v", help="Displays the files generated")],
    with_basic_controller: Annotated[
        bool, Option(False, help="Should generate a basic controller")
    ],
    context: Annotated[
        bool,
        Option(
            False,
            help="Should generate an application with a controller, service, repository, dto.",
        ),
    ],
    version: Annotated[str, Option("v1", help="The API version of the app.")],
    location: Annotated[
        str, Option(".", help="The location where to create the app.", show_default=True)
    ],
) -> None:
    """Creates the scaffold of an application

    How to run: `ravyn createapp <NAME>`

    Example: `ravyn createapp myapp`
    """
    options = {
        "secret_key": SECRET_KEY_INSECURE_PREFIX + get_random_secret_key(),
        "verbosity": verbosity,
        "with_basic_controller": with_basic_controller,
        "simple": False,
        "app_context": context,
        "api_version": version,
        "location": location,
    }
    directive = TemplateDirective()

    for name in names:
        try:
            directive.handle("app", name=name, **options)
            success(f" App {name} generated successfully!")
        except DirectiveError as e:
            error(str(e))
