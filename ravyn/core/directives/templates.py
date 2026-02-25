import os
import shutil
import stat
from importlib import import_module
from pathlib import Path
from typing import Any, Optional, Union

from jinja2 import Environment, FileSystemLoader, Template

import ravyn
from ravyn.core.directives.base import BaseDirective
from ravyn.core.directives.constants import TREAT_AS_PROJECT_DIRECTIVE
from ravyn.core.directives.exceptions import DirectiveError
from ravyn.core.terminal import Print

printer = Print()


class TemplateDirective(BaseDirective):
    """
    Copy either an Ravyn application layout template or an Ravyn project
    layout.
    """

    rewrite_template_suffixes: Any = (
        (".py-tpl", ".py"),
        (".e-tpl", ""),
    )

    def handle(self, app_or_project: str, name: str, **options: Any) -> Any:
        self.app_or_project = app_or_project
        self.name = name
        self.a_or_an = "an" if app_or_project == "app" else "a"
        self.verbosity = options["verbosity"]
        self.with_deployment = options.get("with_deployment", False)
        self.deployment_folder_name = options.get("deployment_folder_name", None)
        self.with_basic_controller = options.get("with_basic_controller", False)
        self.simple = options.get("simple", False)
        self.app_context = options.get("app_context", False)
        self.edgy = options.get("edgy", False)
        self.api_version = options.get("api_version", "v1")
        self.location = os.path.abspath(options.get("location", "."))

        if self.app_or_project not in TREAT_AS_PROJECT_DIRECTIVE:
            self.validate_name(name)
            top_dir = os.path.join(self.location, name)
        else:
            if not self.deployment_folder_name:
                raise DirectiveError("deployment_folder_name is required for project directives")
            top_dir = os.path.join(self.location, self.deployment_folder_name)

        try:
            os.makedirs(top_dir)
        except FileExistsError:
            raise DirectiveError(f"{top_dir} already exists.") from None
        except OSError as e:
            raise DirectiveError(detail=str(e)) from e

        if self.app_or_project not in TREAT_AS_PROJECT_DIRECTIVE:
            base_name = f"{app_or_project}_name"
        else:
            base_name = "project_name"

        base_subdir = f"{app_or_project}_template"
        if self.app_or_project not in TREAT_AS_PROJECT_DIRECTIVE:
            if self.edgy:
                base_subdir = f"{app_or_project}_template_edgy"
            elif self.simple:
                base_subdir = f"{app_or_project}_template_simple"
            elif self.app_context:
                base_subdir = f"{app_or_project}_template_context"
                self.with_basic_controller = True  # noqa

        base_deployment = "deployment_template"

        context = {
            base_name: name,
            "ravyn_version": self.get_version(),
            "project_secret": options.get("secret_key"),
            "deployment_folder": self.deployment_folder_name,
            "with_basic_controller": self.with_basic_controller,
            "name": name,
            "api_version": self.api_version,
        }

        template_dir = os.path.join(ravyn.__path__[0], "conf/directives", base_subdir)
        prefix_length = len(template_dir) + 1

        # Creates the project or application structure
        self.iterate_templates(
            top_dir=top_dir,
            prefix_length=prefix_length,
            name=name,
            base_name=base_name,
            app_or_project=app_or_project,
            template_dir=template_dir,
            context=context,
        )

        # Add deployment files to the project
        if self.with_deployment:
            template_dir = os.path.join(ravyn.__path__[0], "conf/directives", base_deployment)
            prefix_length = len(template_dir) + 1
            self.iterate_templates(
                top_dir=top_dir,
                prefix_length=prefix_length,
                name=name,
                base_name=base_name,
                app_or_project=app_or_project,
                template_dir=template_dir,
                context=context,
                with_deployment=self.with_deployment,
                deployment_folder_name=self.deployment_folder_name,
            )

    def iterate_templates(
        self,
        top_dir: str,
        prefix_length: int,
        name: str,
        base_name: str,
        app_or_project: str,
        template_dir: str,
        context: dict[str, Any],
        with_deployment: bool = False,
        deployment_folder_name: Union[str, None] = None,
    ) -> None:
        """
        Iterates through a specific template directory and populates with the corresponding
        variables
        """
        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]

            relative_dir_template = Template(path_rest.replace(base_name, name))
            relative_dir = relative_dir_template.render(context)

            if with_deployment:
                relative_dir = f"{deployment_folder_name}/{relative_dir}"

            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if dirname.startswith(".") or dirname == "__pycache__":
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith((".pyo", ".pyc", ".py.class")):
                    continue

                old_path = os.path.join(root, filename)
                new_path = os.path.join(top_dir, relative_dir, filename.replace(base_name, name))
                project_dir = os.path.join(top_dir, relative_dir)
                template_name = filename
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[: -len(old_suffix)] + new_suffix
                        template_name = template_name[: -len(old_suffix)] + new_suffix
                        break

                if os.path.exists(new_path):
                    raise DirectiveError(
                        "%s already exists. Overlaying %s %s into an existing "
                        "directory won't replace conflicting files."
                        % (
                            new_path,
                            self.a_or_an,
                            app_or_project,
                        )
                    )

                shutil.copyfile(old_path, new_path)
                if self.verbosity >= 2:
                    printer.write_info("Creating %s" % new_path)
                try:
                    self.manage_template_variables(template_name, new_path, project_dir, context)
                    self.apply_umask(old_path, new_path)
                    self.make_file_writable(new_path)
                except OSError:
                    printer.write_error(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path,
                    )

    def manage_template_variables(
        self,
        template: Union[str, Path],
        destination: Union[str, Path],
        template_dir: Union[str, Path],
        context: dict[str, Any],
    ) -> None:
        """
        Goes through every file generated and replaces the variables with the given
        context variables.
        """
        environment = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = environment.get_template(template)  # type: ignore
        rendered_template = template.render(context)
        if os.path.isfile(destination):
            os.unlink(destination)
        with open(destination, "w") as f:
            f.write(rendered_template)

    def validate_name(self, name: Optional[str], name_or_dir: str = "name") -> None:
        if name is None:
            raise DirectiveError(
                "you must provide {an} {app} name".format(
                    an=self.a_or_an,
                    app=self.app_or_project,
                )
            )
        # Check it's a valid directory name.
        if not name.isidentifier():
            raise DirectiveError(
                "'{name}' is not a valid {app} {type}. Please make sure the "
                "{type} is a valid identifier.".format(
                    name=name,
                    app=self.app_or_project,
                    type=name_or_dir,
                )
            )
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            raise DirectiveError(
                "'{name}' conflicts with the name of an existing Python "
                "module and cannot be used as {an} {app} {type}. Please try "
                "another {type}.".format(
                    name=name,
                    an=self.a_or_an,
                    app=self.app_or_project,
                    type=name_or_dir,
                )
            )

    def apply_umask(self, old_path: Union[str, Path], new_path: Union[str, Path]) -> None:
        current_umask = os.umask(0)
        os.umask(current_umask)
        current_mode = stat.S_IMODE(os.stat(old_path).st_mode)
        os.chmod(new_path, current_mode & ~current_umask)

    def make_file_writable(self, filename: str) -> None:
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)
