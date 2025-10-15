#!/usr/bin/env python
from __future__ import annotations

import os
import shutil
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from multiprocessing import Pool
from pathlib import Path
from typing import Annotated, Any

import click
import mkdocs.commands.build
import mkdocs.commands.serve
import mkdocs.config
import mkdocs.utils
import yaml
from sayer import Option, Sayer, command, error, info, success, warning

mkdocs_name = "mkdocs.yml"

missing_translation_snippet = """
{!../../../docs/missing-translation.md!}
"""

docs_path = Path("docs")
en_docs_path = Path("docs/en")
en_config_path: Path = en_docs_path / mkdocs_name
site_path = Path("site").absolute()

site_lang: str = "site_lang"
build_site_path = Path(site_lang).absolute()


def get_en_config() -> dict[str, Any]:
    """
    Get the English configuration from the specified file.

    Returns:
        A dictionary containing the English configuration.
    """
    return mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))


def get_lang_paths() -> list[Path]:
    """
    Returns a sorted list of paths to language files.

    Returns:
        List[Path]: A sorted list of paths to language files.
    """
    return sorted(docs_path.iterdir())


def complete_existing_lang(incomplete: str):
    """
    Generate a list of existing languages that start with the given incomplete string.

    Args:
        incomplete (str): The incomplete string to match against.

    Yields:
        str: The names of the existing languages that start with the given incomplete string.
    """
    for lang_path in get_lang_paths():
        if lang_path.is_dir() and lang_path.name.startswith(incomplete):
            yield lang_path.name


def get_updated_config_content() -> dict[str, Any]:
    """
    Get the updated configuration content with alternate language links.

    Returns:
        Dict[str, Any]: The updated configuration content.
    """
    config = get_en_config()
    languages = [{"en": "/"}]
    new_alternate: list[dict[str, str]] = []

    # Load local language names from language_names.yml
    language_names_path = Path(__file__).parent / "../docs/language_names.yml"
    local_language_names: dict[str, str] = mkdocs.utils.yaml_load(
        language_names_path.read_text(encoding="utf-8")
    )

    # Add alternate language links to the configuration
    for lang_path in get_lang_paths():
        if lang_path.name in {"en", "em"} or not lang_path.is_dir():
            continue
        code = lang_path.name
        languages.append({code: f"/{code}/"})

    for lang_dict in languages:
        code = list(lang_dict.keys())[0]
        url = lang_dict[code]
        if code not in local_language_names:
            print(f"Missing language name for: {code}, update it in docs/language_names.yml")
            raise click.Abort()
        use_name = f"{code} - {local_language_names[code]}"
        new_alternate.append({"link": url, "name": use_name})

    # Update the configuration with the new alternate links
    config["extra"]["alternate"] = new_alternate

    return config


@command
def update_config() -> None:
    """
    Update the configuration file with the updated content.

    This function reads the English configuration file, generates the updated content
    with alternate language links, and writes it back to the file.

    Returns:
        None
    """
    # Read the English configuration file
    config = get_updated_config_content()

    # Write the updated content to the file
    en_config_path.write_text(
        yaml.dump(config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


def build_site(lang: str = "en") -> None:
    """
    Build the documentation site for a specific language.

    Args:
        lang (str): The language code. Defaults to "en".

    Returns:
        None
    """
    lang_path = Path("docs") / lang
    if not lang_path.is_dir():
        click.echo(f"Language not found: {lang}")
        raise click.Abort()

    click.echo(f"Building site for: {lang}")
    build_site_dist_path = build_site_path / lang
    dist_path = site_path if lang == "en" else site_path / lang

    current_dir = os.getcwd()
    os.chdir(lang_path)
    shutil.rmtree(build_site_dist_path, ignore_errors=True)
    subprocess.run(["mkdocs", "build", "--site-dir", build_site_dist_path], check=True)
    shutil.copytree(build_site_dist_path, dist_path, dirs_exist_ok=True)
    os.chdir(current_dir)
    click.echo(f"Built site for: {lang}")


@command(name="new-lang")
def new_lang(lang: Annotated[str, Option("--l", help="The language to generate", required=True)]):
    """
    Generate a new docs translation directory for the language LANG.

    Args:
        lang (str): The language code.

    Raises:
        click.Abort: If the language directory already exists.

    Returns:
        None
    """
    new_path: Path = Path("docs") / lang
    if new_path.exists():
        info(f"The language was already created: {lang}")
        raise click.Abort()
    new_path.mkdir()
    new_config_path: Path = Path(new_path) / mkdocs_name
    new_config_path.write_text(
        f"INHERIT: ../en/mkdocs.yml\nsite_dir: '../../{site_lang}/{lang}'\n",
        encoding="utf-8",
    )
    new_config_docs_path: Path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path: Path = en_docs_path / "docs" / "index.md"
    new_index_path: Path = new_config_docs_path / "index.md"
    en_index_content = en_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    click.echo(click.style(f"Successfully initialized: {new_path}", fg="green"))
    update_languages.__original_func()


@command(name="build-lang")
def build_lang(lang: Annotated[str, Option("en", "--l", help="The language to generate")]) -> None:
    """
    Build the docs for a language.
    """
    build_site(lang)


@command(name="build-all")
def build_all() -> None:
    """
    Build mkdocs site for each language, resulting in a directory structure
    with each language inside the ./site/ directory.
    """
    # Remove the existing site directory
    shutil.rmtree(site_path, ignore_errors=True)

    # Get a list of all language paths
    lang_paths = [lang.name for lang in get_lang_paths() if lang.is_dir()]

    # Get the number of available CPUs
    cpu_count = os.cpu_count() or 1

    # Set the process pool size to the number of CPUs
    process_pool_size = cpu_count
    info(f"Using process pool size: {process_pool_size}")

    # Create a process pool
    with Pool(process_pool_size) as pool:
        # Build the site for each language in parallel
        pool.map(build_site, lang_paths)


@command(name="update-languages")
def update_languages() -> None:
    """
    Update the mkdocs.yml file Languages section including all the available languages.
    """
    update_config._original_func()


@command
def serve(
    port: Annotated[int, Option(8000, "-p", help="The port to serve the documentation")],
) -> None:
    """
    Serve a built site with translations.

    This command is used to preview a site with translations that have already been built.
    It starts a simple server to serve the site on the specified port.

    Args:
        port (int): The port number to serve the documentation. Defaults to 8000.

    Returns:
        None
    """
    warning("Warning: this is a very simple server.")
    info("For development, use the command live instead.")
    info("This is here only to preview a site with translations already built.")
    info("Make sure you run the build-all command first.")
    os.chdir("site")
    server_address = ("", port)
    server = HTTPServer(server_address, SimpleHTTPRequestHandler)
    success(f"Serving at: http://127.0.0.1:{port}")
    server.serve_forever()


@command
def live(
    lang: Annotated[
        str,
        Option(
            "en",
            "--l",
            help="The language to generate",
        ),
    ],
    port: Annotated[int, Option(8000, "-p", help="The port to serve the documentation")],
) -> None:
    """
    Serve a docs site with livereload for a specific language.

    This command starts a server with livereload to serve the translated files for a specific language.
    It only shows the actual translated files, not the placeholders created with build-all.

    Args:
        lang (str): The language code. Defaults to 'en'.
        port (int): The port number to serve the documentation. Defaults to 8000.

    Returns:
        None
    """
    click.echo("Warning: this is a very simple server.")
    lang_path: Path = docs_path / lang
    os.chdir(lang_path)
    mkdocs.commands.serve.serve(dev_addr=f"127.0.0.1:{port}")


@command(name="verify-config")
def verify_config() -> None:
    """
    Verify the main mkdocs.yml content to ensure it uses the latest language names.

    This function compares the current English configuration with the updated configuration
    that includes the latest language names. If they are different, it raises an error
    and prompts the user to update the language names in the language_names.yml file.

    Returns:
        None
    """
    info("Verifying mkdocs.yml")
    config = get_en_config()
    updated_config = get_updated_config_content()
    if config != updated_config:
        error(
            click.style(
                "docs/en/mkdocs.yml is outdated from docs/language_names.yml. "
                "Please update language_names.yml and run 'python ./scripts/docs.py update-languages'.",
                fg="red",
            )
        )
        raise click.Abort()
    click.echo("Valid mkdocs.yml ✅")


docs_cli = Sayer(name="docs", help="The documentation generator", invoke_without_command=True)
docs_cli.add_command(build_all)
docs_cli.add_command(serve)
docs_cli.add_command(live)
docs_cli.add_command(verify_config)
docs_cli.add_command(update_languages)
docs_cli.add_command(update_config)

if __name__ == "__main__":
    docs_cli()
