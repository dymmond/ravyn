from pathlib import Path
from typing import Any, Optional, Tuple, Union

from lilya._internal._path import clean_path
from lilya.staticfiles import StaticFiles
from lilya.types import ASGIApp
from pydantic import BaseModel, DirectoryPath, StringConstraints, field_validator
from typing_extensions import Annotated, Doc

DirectoryType = Union[DirectoryPath, str, Path, Any]


class StaticFilesConfig(BaseModel):
    """
    An instance of [StaticFilesConfig](https://ravyn.dev/configurations/staticfiles/).

    This configuration is used to enable and serve static files via
    Ravyn application.

    **Example**

    ```python
    from ravyn import Ravyn
    from ravyn.config import StaticFilesConfig

    static_files_config = StaticFilesConfig(
        path="/static", directory=Path("static")
    )

    app = Ravyn(static_files_config=static_files_config)
    # or multiple in descending priority
    app = Ravyn(static_files_config=[static_files_config1, static_files_config2, ...])

    ```
    """

    path: Annotated[  # type: ignore
        str,
        StringConstraints(min_length=1),
        Doc(
            """
            The path for the statics.
            """
        ),
    ]
    directory: Annotated[
        Optional[Union[DirectoryType, list[DirectoryType], tuple[DirectoryType, ...]]],
        Doc(
            """
            The directory for the statics in the format of a path like.

            Example: `/static`.
            """
        ),
    ] = None
    html: Annotated[
        bool,
        Doc(
            """
            Run in HTML mode. Automatically loads index.html for directories if such file exist.
            """
        ),
    ] = False
    packages: Annotated[
        Optional[list[Union[str, Tuple[str, str]]]],
        Doc(
            """
            A list of strings or list of tuples of strings of python packages.
            """
        ),
    ] = None
    check_dir: Annotated[
        bool,
        Doc(
            """
            Ensure that the directory exists upon instantiation.
            """
        ),
    ] = True
    name: Annotated[
        Optional[str],
        Doc(
            """
            The name of the static files to be looked up at.
            """
        ),
    ] = None

    fall_through: Annotated[
        bool,
        Doc(
            """
            Activate fall-through routing.
            """
        ),
    ] = False
    follow_symlink: Annotated[
        bool,
        Doc(
            """
            Follow symlinks.
            """
        ),
    ] = False

    @field_validator("path")
    def validate_path(cls, value: str) -> str:
        if "{" in value:
            raise ValueError("path parameters are not supported for static files")
        return clean_path(value)

    def to_app(self) -> ASGIApp:
        """
        It can be three scenarios
        """

        return StaticFiles(**self.model_dump(exclude_none=True, exclude=["path", "name"]))  # type: ignore
