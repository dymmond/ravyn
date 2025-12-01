import contextlib
import functools
import importlib
import os
import pkgutil
import sys
import typing
from difflib import get_close_matches
from importlib import import_module
from pathlib import Path
from typing import Any, Optional

from sayer import error

from ravyn.core.directives.base import BaseDirective
from ravyn.core.directives.exceptions import DirectiveError
from ravyn.core.terminal import Print

printer = Print()

IGNORE_FOLDERS = ["__pycache__"]
OPERATIONS = "operations"

EXCUDED_DIRECTIVES = ["list", "run"]


def find_directives(management_dir: str) -> list[str]:
    """
    Shows the available directives from Ravyn.
    """
    directive_dir = os.path.join(management_dir, "operations")
    directive_list = []
    for _, name, is_package in pkgutil.iter_modules([directive_dir]):
        if not is_package and not name.startswith("_"):
            if name not in EXCUDED_DIRECTIVES:
                directive_list.append(name)
    return directive_list


def find_application_directives(
    management_dir: str,
) -> typing.Sequence[dict[Any, Any] | str]:
    """
    Iterates through the application tree and finds the directives available
    to run.
    """
    directive_list = []
    for root, folders, _ in os.walk(management_dir):
        if OPERATIONS not in folders:
            continue

        directive_dir = os.path.join(root, "operations")
        for location, name, is_package in pkgutil.iter_modules([directive_dir]):
            if not is_package and not name.startswith("_"):
                directive_list.append({"name": name, "location": location.path})
    return directive_list


def load_directive_class(app_name: str, name: str) -> Any:
    """
    Loads the directive class from native Ravyn.
    """
    module = import_module("{}.directives.operations.{}".format(app_name, name))
    return module.Directive()


def load_directive_class_by_filename(app_name: str, location: str, skip_exit: bool = False) -> Any:
    """
    Loads the directive by filename.

    Passing a name a location, dynamically searches for the directive python file
    and loads it.
    """
    spec = importlib.util.spec_from_file_location(app_name, location)
    if not spec or spec is None:
        error(f"{app_name} not found")
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # If it exports a class called Directive
    if hasattr(module, "Directive"):
        return module.Directive()

    # Support: `@directive @command` function
    for attr in dir(module):
        obj = getattr(module, attr)
        if callable(obj) and getattr(obj, "__is_custom_directive__", False):
            return obj

    if not skip_exit:
        error(f"No directive found in {app_name}")
        sys.exit(1)


@functools.lru_cache(maxsize=None)
def get_directives(location: str) -> typing.Sequence[dict[Any, Any] | str]:
    command_list = find_directives(location)
    directives = []

    for name in command_list:
        directives.append({name: "ravyn.core", "location": None})
    return directives


@functools.lru_cache(maxsize=None)
def get_application_directives(
    location: str,
) -> typing.Sequence[dict[Any, Any]]:
    command_list = find_application_directives(location)
    directives = []

    for value in command_list:
        directives.append(
            {value["name"]: "application", "location": value["location"], "name": value["name"]}  # type: ignore
        )
    return directives


def fetch_custom_directive(subdirective: Any, location: Optional[str]) -> Any:
    """Fetches the directive classes custom and native"""
    directives = get_application_directives(location)

    counter = 0
    matches = []
    app_name = None

    for directive in sorted(directives, key=lambda d: d["location"]):
        try:
            for key, _ in directive.items():
                if key == subdirective:
                    app_name = key
                    location = directive["location"]
                    break
        except KeyError:
            counter += 1
            directive = {k: v for k, v in directive.items() if k != "location"}
            matches.extend(get_close_matches(subdirective, directive))

            if matches and len(directives) == counter:
                error("Did you mean %s?" % matches[0])

            if len(directives) == counter:
                return None
            continue

    if not app_name:
        directive = {k: v for k, v in directive.items() if k != "location"}
        matches.extend(get_close_matches(subdirective, directive))

        if matches:
            error("Did you mean %s?" % matches[0])
            return None
        return None

    name = f"{location}/{app_name}.py"
    klass = load_directive_class_by_filename(app_name, name)

    if not isinstance(klass, BaseDirective) and not getattr(
        klass, "__is_custom_directive__", False
    ):
        raise DirectiveError(
            detail="The directive must be a subclass of BaseDirective or marked with @directive"
        )
    return klass


def fetch_directive(subdirective: Any, location: Optional[str], is_custom: bool = False) -> Any:
    """Fetches the directive classes custom and native"""
    if not is_custom:
        directives = get_directives(location)
    else:
        return fetch_custom_directive(subdirective, location)

    counter = 0
    matches = []

    for directive in directives:
        try:
            app_name = directive[subdirective]
        except KeyError:
            counter += 1

            directive = {k: v for k, v in directive.items() if k != "location"}
            matches.extend(get_close_matches(subdirective, directive))

            if matches and len(directives) == counter:
                error("Did you mean %s?" % matches[0])

            if len(directives) == counter:
                return None
            continue

    if isinstance(app_name, BaseDirective):
        klass = app_name
    else:
        klass = load_directive_class(app_name, subdirective)
    return klass


def fetch_custom_directive_by_location(location: str) -> Any:
    """
    Load a directive class from a file path and return it ONLY if it is marked
    with `__is_custom_directive__`. Otherwise, return None.
    Parameters:
        location (str): Absolute or relative path to a Python file (e.g. ".../createsuperuser.py").
    Returns:
        Any: The loaded directive class if it has `__is_custom_directive__`, else None.
    Raises:
        DirectiveError: If the location does not exist, is not a .py file, or loading fails.
    """
    path = Path(location)

    if not path.exists():
        error(f"Directive location not found: {location}")
        raise DirectiveError(f"Directive location not found: {location}")

    if path.is_dir():
        error(f"Expected a .py file, got directory: {location}")
        raise DirectiveError(f"Expected a .py file, got directory: {location}")

    if path.suffix != ".py":
        error(f"Expected a .py file, got: {location}")
        raise DirectiveError(f"Expected a .py file, got: {location}")

    app_name = path.stem

    try:
        klass = load_directive_class_by_filename(app_name, str(path), skip_exit=True)
    except TypeError:
        raise
    except Exception as exc:  # be specific if you have custom exceptions
        message = f"Failed to load directive from {location}: {exc}"
        raise DirectiveError(message) from exc

    # Only accept classes explicitly marked as custom directives.
    if getattr(klass, "__is_custom_directive__", False):
        return klass
    return None


def get_custom_directives_to_cli(location: str) -> dict:
    """
    Scans the given application location for custom CLI directives and adds them to the main Lilya CLI.
    This function looks for directive definitions in the specified location, attempts to load them,
    and returns a dictionary mapping directive names to their corresponding command implementations.
    Parameters:
        location (str): The root path of the application where custom directives are defined.
    Returns:
        dict: A dictionary where keys are directive names and values are the corresponding command objects.
              If no valid directives are found, an empty dictionary is returned.
    Raises:
        DirectiveError: If a directive cannot be loaded due to an error in its definition or location.
                        These errors are silently ignored in this implementation.
    """
    directives = {}

    application_directives = get_application_directives(location)

    for directive in application_directives:
        name = directive["name"]
        directive_location = directive["location"]

        directive_location = f"{directive_location}/{name}.py"

        with contextlib.suppress(DirectiveError):
            command = fetch_custom_directive_by_location(directive_location)
            if command is not None and command.__display_in_cli__:
                directives[name] = command
                continue
    return directives
