import datetime
from collections import OrderedDict
from typing import Any

import lilya
import lilya.compat
import pydantic
from monkay import load

import ravyn
import ravyn.openapi.datastructures
import ravyn.routing.gateways
import ravyn.routing.router
from ravyn.core.terminal import OutputColour, Print

printer = Print()

defaults = OrderedDict()

defaults.update(
    {
        "datetime": datetime,
        "timedelta": datetime,
        "BaseModel": pydantic,
        "FieldInfo": pydantic.fields,
        "Field": pydantic.fields,
        "ConfigDict": pydantic,
        "reverse": lilya.compat,
        "settings": ravyn,
        "Body": ravyn.params,
        "File": ravyn.params,
        "Param": ravyn.params,
        "OpenAPIResponse": ravyn.openapi.datastructures,
        "Gateway": ravyn.routing.gateways,
        "WebSocketGateway": ravyn.routing.gateways,
        "Include": ravyn.routing.router,
        "Router": ravyn.routing.router,
        "HTTPHandler": ravyn.routing.router,
        "WebSocketHandler": ravyn.routing.router,
    }
)


def welcome_message(app: Any) -> None:
    """Displays the welcome message for the user"""
    now = datetime.datetime.now().strftime("%b %d %Y, %H:%M:%S")
    ravyn_info_date = f"Ravyn {ravyn.__version__} (interactive shell, {now})"
    info = "Interactive shell that imports the application defaults."

    application_text = printer.message(f"{app.app_name}, version: ", colour=OutputColour.CYAN3)
    application_name = printer.message(app.version, colour=OutputColour.GREEN3)
    application = f"{application_text}{application_name}"

    printer.write_plain(ravyn_info_date, colour=OutputColour.CYAN3)
    printer.write_plain(info, colour=OutputColour.CYAN3)
    printer.write_plain(application)


def import_objects(app: Any) -> dict[Any, Any]:
    """
    Imports all the needed objects needed for the shell.
    """
    imported_objects = {}
    filtered_defaults: dict[Any, Any] = {}
    import_statement = "from {module_path} import {model}"

    welcome_message(app)
    printer.write_success(79 * "-", colour=OutputColour.CYAN3)

    def extract_same_module_objects() -> None:
        for key, value in defaults.items():
            filtered_defaults.setdefault(value, set()).add(key)

    def import_defaults() -> None:
        for module, name_set in filtered_defaults.items():
            is_module: bool = True
            names = ", ".join(sorted(name_set))
            try:
                directive = import_statement.format(module_path=module.__module__, model=names)
            except AttributeError:
                directive = import_statement.format(module_path=module.__name__, model=names)
                is_module = False

            printer.write_success(directive, colour=OutputColour.CYAN3)

            for name in name_set:
                if is_module:
                    imported_objects[name] = module
                else:
                    dotted_path = f"{module.__name__}.{name}"
                    class_object = load(dotted_path)
                    imported_objects[name] = class_object

    extract_same_module_objects()
    import_defaults()
    return imported_objects
