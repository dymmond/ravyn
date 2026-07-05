# `BaseController` class

This is the reference for the `BaseController` that contains all the parameters,
attributes and functions.

The `BaseController` serves as the base of all object-oriented views of [Ravyn](../ravyn.md) such as
[`Controller`](#ravyn.Controller), [`SimpleAPIController`](#ravyn.SimpleAPIController) and all the generics.

::: ravyn.routing.controllers.BaseController
    options:
        filters:

        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.Controller
    options:
        filters:

        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.SimpleAPIController
    options:
        filters:

        - "!^__slots__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.routing.controllers.generics.CreateAPIController
    options:
        filters:

        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"

::: ravyn.routing.controllers.generics.ReadAPIController
    options:
        filters:

        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.controllers.generics.DeleteAPIController
    options:
        filters:

        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"

::: ravyn.routing.controllers.generics.ListAPIController
    options:
        filters:

        - "!^__slots__"
        - "!^__is_generic__"
        - "!^get_filtered_handler"
        - "!^get_route_handlers"
        - "!^handle"
        - "!^create_signature_model"
        - "!^is_signature_valid"
