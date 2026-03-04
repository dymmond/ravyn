#!/usr/bin/env python
from __future__ import annotations

import copy
import shutil
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Annotated

import click
import yaml
from sayer import Option, Sayer, command, error, info, success, warning

try:
    from scripts.docs_pipeline import (
        MARKDOWN_SUFFIXES,
        DocsPipelineError,
        render_markdown_with_includes,
        run_zensical,
    )
except ModuleNotFoundError:  # pragma: no cover
    from docs_pipeline import (  # type: ignore[no-redef]
        MARKDOWN_SUFFIXES,
        DocsPipelineError,
        render_markdown_with_includes,
        run_zensical,
    )

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"
EN_DOCS_DIR = DOCS_DIR / "en" / "docs"
DOCS_SRC_DIR = ROOT_DIR / "docs_src"
BASE_CONFIG_FILE = DOCS_DIR / "en" / "mkdocs.yaml"
LANGUAGE_NAMES_FILE = DOCS_DIR / "language_names.yml"
MISSING_TRANSLATION_FILE = DOCS_DIR / "missing-translation.md"

FINAL_SITE_DIR = ROOT_DIR / "site"

SITE_LANG_DIR = ROOT_DIR / "site_lang"
MKDOCS_CONFIG_NAME = "mkdocs.yaml"
LANG_BUILD_CONFIG_NAME = MKDOCS_CONFIG_NAME
LANG_GENERATED_DIR_NAME = "generated"
LANG_SITE_DIR_NAME = "site"
MISSING_TRANSLATION_INCLUDE = "{!../../../docs/missing-translation.md!}"
NON_TRANSLATED_SECTIONS = ("reference/", "release-notes.md")


def _language_generated_docs_dir(lang: str) -> Path:
    return DOCS_DIR / lang / LANG_GENERATED_DIR_NAME


def _language_built_site_dir(lang: str) -> Path:
    return DOCS_DIR / lang / LANG_SITE_DIR_NAME


def _language_build_config_file(lang: str) -> Path:
    return DOCS_DIR / lang / LANG_BUILD_CONFIG_NAME


def _snapshot(paths: list[Path]) -> dict[str, int]:
    state: dict[str, int] = {}
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            state[str(path.resolve())] = path.stat().st_mtime_ns
            continue
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file():
                state[str(candidate.resolve())] = candidate.stat().st_mtime_ns
    return state


def _read_yaml(path: Path) -> dict:
    content = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.Loader)  # noqa: S506
    if content is None:
        return {}
    if not isinstance(content, dict):
        raise click.ClickException(f"Expected YAML mapping in {path}")
    return content


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(data, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


def _get_site_url() -> str:
    en_config = _read_yaml(BASE_CONFIG_FILE)
    site_url = en_config.get("site_url", "")
    if not isinstance(site_url, str):
        return ""
    return site_url.rstrip("/")


def _clean_markdown_extensions(extensions: list | None) -> list:
    if not extensions:
        return []

    cleaned: list = []
    for entry in extensions:
        if isinstance(entry, str):
            if entry == "mdx_include":
                continue
            if entry == "extra":
                # Avoid order-sensitive conflicts between `extra` (which enables
                # fenced_code) and SuperFences under Zensical's extension
                # normalization. Keep the useful parts explicitly.
                cleaned.extend(["abbr", "def_list", "footnotes"])
                continue
            cleaned.append(entry)
            continue

        if not isinstance(entry, dict):
            cleaned.append(copy.deepcopy(entry))
            continue

        name, value = next(iter(entry.items()))
        if name == "mdx_include":
            continue

        if name == "pymdownx.superfences" and isinstance(value, dict):
            fences = value.get("custom_fences")
            if isinstance(fences, list):
                for fence in fences:
                    if isinstance(fence, dict):
                        fence.pop("format", None)

        cleaned.append({name: copy.deepcopy(value)})

    return cleaned


def _get_language_paths() -> list[Path]:
    language_paths: list[Path] = []
    for path in sorted(DOCS_DIR.iterdir()):
        if not path.is_dir():
            continue
        if path.name in {"generated"}:
            continue
        if path.name.startswith("."):
            continue
        if not (path / "docs").is_dir():
            continue
        if not (path / MKDOCS_CONFIG_NAME).is_file():
            continue
        language_paths.append(path)

    language_paths.sort(key=lambda item: (item.name != "en", item.name))
    return language_paths


def _get_languages() -> list[str]:
    return [path.name for path in _get_language_paths()]


def complete_existing_lang(incomplete: str):
    for language in _get_languages():
        if language.startswith(incomplete):
            yield language


def _read_language_names() -> dict[str, str]:
    raw = _read_yaml(LANGUAGE_NAMES_FILE)
    normalized: dict[str, str] = {}
    for code, name in raw.items():
        normalized[str(code)] = str(name)
    return normalized


def _build_alternates(languages: list[str]) -> list[dict[str, str]]:
    language_names = _read_language_names()
    alternates: list[dict[str, str]] = []
    for lang in languages:
        if lang not in language_names:
            raise click.ClickException(
                f"Missing language name for '{lang}'. Update {LANGUAGE_NAMES_FILE}."
            )
        link = "/" if lang == "en" else f"/{lang}/"
        alternates.append({"link": link, "name": f"{lang} - {language_names[lang]}", "lang": lang})
    return alternates


def _ensure_valid_languages() -> tuple[list[str], list[dict[str, str]]]:
    languages = _get_languages()
    if not languages:
        raise click.ClickException(f"No language docs found under {DOCS_DIR}")
    if "en" not in languages:
        raise click.ClickException("English docs directory (docs/en/) is required.")
    alternates = _build_alternates(languages)
    return languages, alternates


def _collect_files(base_dir: Path) -> dict[Path, Path]:
    files: dict[Path, Path] = {}
    if not base_dir.is_dir():
        return files
    for file_path in sorted(base_dir.rglob("*")):
        if not file_path.is_file():
            continue
        relative = file_path.relative_to(base_dir)
        files[relative] = file_path
    return files


def _should_inject_missing_translation(relative_path: Path) -> bool:
    path_str = relative_path.as_posix()
    return not any(path_str.startswith(section) for section in NON_TRANSLATED_SECTIONS)


def _inject_missing_translation_notice(markdown: str, snippet: str) -> str:
    header = ""
    body = markdown
    if markdown.startswith("#"):
        header, _, body = markdown.partition("\n\n")
    return f"{header}\n\n{snippet}\n\n{body}"


def _render_language_docs(lang: str) -> Path:
    en_files = _collect_files(EN_DOCS_DIR)
    lang_docs_dir = DOCS_DIR / lang / "docs"
    lang_files = _collect_files(lang_docs_dir) if lang != "en" else {}

    union = sorted(set(en_files).union(lang_files))
    output_dir = _language_generated_docs_dir(lang)
    tmp_output_dir = output_dir.parent / f".{output_dir.name}.tmp"
    if tmp_output_dir.exists():
        shutil.rmtree(tmp_output_dir)
    tmp_output_dir.mkdir(parents=True, exist_ok=True)

    missing_translation_snippet = MISSING_TRANSLATION_FILE.read_text(encoding="utf-8").strip()

    for relative in union:
        source = lang_files.get(relative) or en_files.get(relative)
        if source is None:
            continue

        target = tmp_output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)

        if source.suffix.lower() in MARKDOWN_SUFFIXES:
            markdown = source.read_text(encoding="utf-8")
            if (
                lang != "en"
                and relative not in lang_files
                and _should_inject_missing_translation(relative)
            ):
                markdown = _inject_missing_translation_notice(
                    markdown, missing_translation_snippet
                )
            include_base_dir = lang_docs_dir if relative in lang_files else EN_DOCS_DIR
            rendered = render_markdown_with_includes(markdown, source, include_base_dir)
            target.write_text(rendered, encoding="utf-8")
        else:
            shutil.copy2(source, target)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    tmp_output_dir.replace(output_dir)
    return output_dir


def _prepare_languages(languages: list[str]) -> None:
    for lang in languages:
        generated_path = _render_language_docs(lang)
        info(f"Prepared {lang} docs in {generated_path}")


def _build_language_config(lang: str, alternates: list[dict[str, str]]) -> Path:
    config_path = _language_build_config_file(lang)
    site_url = _get_site_url()
    lang_site_url = site_url if lang == "en" else f"{site_url}/{lang}" if site_url else ""

    config = copy.deepcopy(_read_yaml(BASE_CONFIG_FILE))
    config["docs_dir"] = LANG_GENERATED_DIR_NAME
    config["site_dir"] = LANG_SITE_DIR_NAME
    config.pop("hooks", None)

    theme = config.setdefault("theme", {})
    if not isinstance(theme, dict):
        raise click.ClickException("Expected 'theme' to be a mapping in docs/en/mkdocs.yaml")
    theme["language"] = lang
    theme["custom_dir"] = str(Path("..") / "en" / "overrides")

    extensions = config.get("markdown_extensions")
    if isinstance(extensions, list):
        config["markdown_extensions"] = _clean_markdown_extensions(extensions)

    extra = config.setdefault("extra", {})
    if not isinstance(extra, dict):
        raise click.ClickException("Expected 'extra' to be a mapping in docs/en/mkdocs.yaml")
    extra["alternate"] = alternates

    if lang_site_url:
        config["site_url"] = lang_site_url

    _write_yaml(config_path, config)
    return config_path


def _assemble_site_for_all_languages(languages: list[str]) -> None:
    shutil.rmtree(FINAL_SITE_DIR, ignore_errors=True)

    en_built = _language_built_site_dir("en")
    if not en_built.is_dir():
        raise click.ClickException(f"Missing built English site at {en_built}")
    shutil.copytree(en_built, FINAL_SITE_DIR)

    for lang in languages:
        if lang == "en":
            continue
        built_lang = _language_built_site_dir(lang)
        if not built_lang.is_dir():
            raise click.ClickException(f"Missing built site for language '{lang}' at {built_lang}")
        target = FINAL_SITE_DIR / lang
        shutil.copytree(built_lang, target)


def _assemble_site_for_single_language(lang: str) -> None:
    built_lang = _language_built_site_dir(lang)
    if not built_lang.is_dir():
        raise click.ClickException(f"Missing built site for language '{lang}' at {built_lang}")

    if lang == "en":
        FINAL_SITE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copytree(built_lang, FINAL_SITE_DIR, dirs_exist_ok=True)
        return

    target = FINAL_SITE_DIR / lang
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built_lang, target, dirs_exist_ok=True)


def _build_languages(
    languages: list[str], clean_cache: bool, alternates: list[dict[str, str]]
) -> None:
    for index, lang in enumerate(languages):
        config_file = _build_language_config(lang, alternates)
        shutil.rmtree(_language_built_site_dir(lang), ignore_errors=True)
        run_zensical(
            project_root=ROOT_DIR,
            config_file=config_file,
            command="build",
            clean=clean_cache if index == 0 else False,
        )


def _watch_language_sources(
    stop_event: threading.Event,
    lang: str,
    alternates: list[dict[str, str]],
    interval: float = 0.5,
) -> None:
    watch_paths = [EN_DOCS_DIR, DOCS_SRC_DIR]
    if lang != "en":
        watch_paths.append(DOCS_DIR / lang / "docs")
    previous = _snapshot(watch_paths)
    while not stop_event.wait(interval):
        current = _snapshot(watch_paths)
        if current == previous:
            continue
        previous = current
        try:
            _prepare_languages([lang])
            _build_language_config(lang, alternates)
            success(f"Refreshed docs sources for {lang} ✅")
        except (DocsPipelineError, click.ClickException) as exc:
            click.echo(f"Docs refresh failed: {exc}", err=True)


def _watch_all_language_sources(
    stop_event: threading.Event,
    languages: list[str],
    alternates: list[dict[str, str]],
    interval: float = 0.5,
) -> None:
    watch_paths = [EN_DOCS_DIR, DOCS_SRC_DIR]
    for lang in languages:
        lang_docs = DOCS_DIR / lang / "docs"
        if lang_docs not in watch_paths:
            watch_paths.append(lang_docs)
    previous = _snapshot(watch_paths)
    while not stop_event.wait(interval):
        current = _snapshot(watch_paths)
        if current == previous:
            continue
        previous = current
        try:
            _prepare_languages(languages)
            _build_languages(languages, clean_cache=False, alternates=alternates)
            _assemble_site_for_all_languages(languages)
            success("Refreshed docs sources for all languages ✅")
        except (DocsPipelineError, click.ClickException) as exc:
            click.echo(f"Docs refresh failed: {exc}", err=True)


def _serve_static_site(port: int) -> None:
    if not FINAL_SITE_DIR.is_dir():
        raise click.ClickException(f"Build output not found: {FINAL_SITE_DIR}")

    info(f"Serving static docs from {FINAL_SITE_DIR}")
    handler = partial(SimpleHTTPRequestHandler, directory=str(FINAL_SITE_DIR))
    server = HTTPServer(("", port), handler)
    success(f"Serving at: http://127.0.0.1:{port}")
    server.serve_forever()


@command
def prepare() -> None:
    """Generate build-ready docs for all languages."""
    languages, _ = _ensure_valid_languages()
    _prepare_languages(languages)
    success("Docs prepared ✅")


@command
def clean() -> None:
    """Remove generated docs artifacts and build output."""
    for path in [
        DOCS_DIR / "generated",
        ROOT_DIR / ".cache" / "docs-sites",
        FINAL_SITE_DIR,
        SITE_LANG_DIR,
    ]:
        shutil.rmtree(path, ignore_errors=True)
    for lang_path in _get_language_paths():
        shutil.rmtree(lang_path / LANG_GENERATED_DIR_NAME, ignore_errors=True)
        shutil.rmtree(lang_path / LANG_SITE_DIR_NAME, ignore_errors=True)
        shutil.rmtree(lang_path / ".generated", ignore_errors=True)
        shutil.rmtree(lang_path / ".site", ignore_errors=True)
    success("Removed docs artifacts ✅")


@command(name="update-languages")
def update_languages() -> None:
    """Validate language directories and language names."""
    languages, alternates = _ensure_valid_languages()
    info(f"Detected languages: {', '.join(languages)}")
    info(f"Generated alternate links: {', '.join(item['link'] for item in alternates)}")
    success("Language metadata is valid ✅")


@command(name="build-lang")
def build_lang(
    lang: Annotated[
        str,
        Option(
            "en",
            "--lang",
            "--l",
            help="Language code to build",
        ),
    ],
    clean_cache: Annotated[
        bool,
        Option(False, "--clean", help="Clean Zensical cache before build.", is_flag=True),
    ] = False,
) -> None:
    """Build documentation for a single language and merge into ./site."""
    languages, alternates = _ensure_valid_languages()
    if lang not in languages:
        raise click.ClickException(f"Language not found: {lang}")

    _prepare_languages([lang])
    _build_languages([lang], clean_cache, alternates)
    _assemble_site_for_single_language(lang)
    success(f"Docs built for language '{lang}' ✅")


@command
def build(
    clean_cache: Annotated[
        bool,
        Option(False, "--clean", help="Clean Zensical cache before build.", is_flag=True),
    ] = False,
) -> None:
    """Build all languages and assemble final site output."""
    languages, alternates = _ensure_valid_languages()
    _prepare_languages(languages)
    _build_languages(languages, clean_cache, alternates)
    _assemble_site_for_all_languages(languages)
    success("Docs built for all languages ✅")


@command(name="new-lang")
def new_lang(
    lang: Annotated[
        str,
        Option(
            "--lang",
            "--l",
            help="Language code to create",
            required=True,
        ),
    ],
) -> None:
    """Create a new docs language directory scaffold."""
    new_path = DOCS_DIR / lang
    if new_path.exists():
        raise click.ClickException(f"The language already exists: {lang}")

    new_docs_path = new_path / "docs"
    new_docs_path.mkdir(parents=True, exist_ok=False)

    new_config_path = new_path / MKDOCS_CONFIG_NAME
    new_config_path.write_text(
        f"INHERIT: ../en/{MKDOCS_CONFIG_NAME}\nsite_dir: '../../site_lang/{lang}'\n",
        encoding="utf-8",
    )

    en_index = EN_DOCS_DIR / "index.md"
    new_index = new_docs_path / "index.md"
    new_index.write_text(
        f"{MISSING_TRANSLATION_INCLUDE}\n\n{en_index.read_text(encoding='utf-8')}",
        encoding="utf-8",
    )

    success(f"Successfully initialized: {new_path}")
    try:
        update_languages.__original_func()
    except click.ClickException:
        warning(
            f"Language scaffold created for '{lang}', but {LANGUAGE_NAMES_FILE} is missing "
            f"an entry for this language."
        )


@command
def serve(
    lang: Annotated[
        str,
        Option(
            "en",
            "--lang",
            "--l",
            help="Language code to serve",
        ),
    ],
    port: Annotated[int, Option(8000, "-p", help="Port to serve documentation")],
    open_browser: Annotated[
        bool,
        Option(False, "--open", help="Open docs in default browser.", is_flag=True),
    ] = False,
    watch_sources: Annotated[
        bool,
        Option(
            True,
            help="Watch docs sources and refresh generated docs while serving.",
        ),
    ] = True,
    serve_all: Annotated[
        bool,
        Option(
            False,
            "--all",
            help="Build all languages and serve the merged static site.",
            is_flag=True,
        ),
    ] = False,
    single_lang: Annotated[
        bool,
        Option(
            False,
            "--single-lang",
            help="Serve a single language in live mode. Useful for focused authoring.",
            is_flag=True,
        ),
    ] = False,
) -> None:
    """Serve docs in live mode for one language, or static merged mode for all."""
    languages, alternates = _ensure_valid_languages()

    if serve_all and single_lang:
        raise click.ClickException("Choose either --all or --single-lang, not both.")

    if not serve_all and not single_lang and len(languages) > 1:
        info(
            "Multiple languages detected; serving all languages so the language selector "
            "works locally. Use --single-lang to serve one language."
        )
        serve_all = True

    if serve_all:
        _prepare_languages(languages)
        _build_languages(languages, clean_cache=False, alternates=alternates)
        _assemble_site_for_all_languages(languages)

        stop_event = threading.Event()
        watch_thread: threading.Thread | None = None
        if watch_sources:
            watched_docs_dirs = [EN_DOCS_DIR]
            watched_docs_dirs.extend(
                path
                for path in (DOCS_DIR / item / "docs" for item in languages)
                if path != EN_DOCS_DIR
            )
            watched_paths = [EN_DOCS_DIR, DOCS_SRC_DIR, *watched_docs_dirs[1:]]
            watch_thread = threading.Thread(
                target=_watch_all_language_sources,
                args=(stop_event, languages, alternates),
                daemon=True,
            )
            watch_thread.start()
            info(
                "Watching source docs for changes: "
                + ", ".join(str(path) for path in watched_paths)
            )
        try:
            _serve_static_site(port=port)
        finally:
            stop_event.set()
            if watch_thread is not None:
                watch_thread.join(timeout=1.0)
        return

    if lang not in languages:
        raise click.ClickException(f"Language not found: {lang}")

    _prepare_languages([lang])
    config_file = _build_language_config(lang, alternates)

    stop_event = threading.Event()
    watch_thread: threading.Thread | None = None

    if watch_sources:
        watched_paths = [EN_DOCS_DIR, DOCS_SRC_DIR]
        if lang != "en":
            watched_paths.insert(1, DOCS_DIR / lang / "docs")
        watch_thread = threading.Thread(
            target=_watch_language_sources,
            args=(stop_event, lang, alternates),
            daemon=True,
        )
        watch_thread.start()
        info("Watching source docs for changes: " + ", ".join(str(path) for path in watched_paths))

    try:
        run_zensical(
            project_root=ROOT_DIR,
            config_file=config_file,
            command="serve",
            dev_addr=f"127.0.0.1:{port}",
            open_browser=open_browser,
        )
    finally:
        stop_event.set()
        if watch_thread is not None:
            watch_thread.join(timeout=1.0)


@command(name="serve-lang")
def serve_lang(
    lang: Annotated[
        str,
        Option(
            "en",
            "--lang",
            "--l",
            help="Language code to serve",
        ),
    ],
    port: Annotated[int, Option(8000, "-p", help="Port to serve documentation")],
) -> None:
    """Alias for serve --lang."""
    serve.__original_func(
        lang=lang,
        port=port,
        open_browser=False,
        watch_sources=True,
        serve_all=False,
        single_lang=True,
    )


@command
def dev(
    port: Annotated[int, Option(8000, "-p", help="Port to serve the built site")],
) -> None:
    """Serve the already-built multi-language site."""
    warning("Warning: this is a simple static file server.")
    info("Run 'hatch run docs:build' first for a full multi-language preview.")
    _serve_static_site(port=port)


@command(name="verify-config")
def verify_config() -> None:
    """Compatibility command that validates language metadata."""
    try:
        update_languages.__original_func()
        click.echo("Valid language configuration ✅")
    except click.ClickException as exc:
        error(click.style(str(exc), fg="red"))
        raise


docs_cli = Sayer(name="docs", help="The documentation generator", invoke_without_command=True)
docs_cli.add_command(prepare)
docs_cli.add_command(clean)
docs_cli.add_command(update_languages)
docs_cli.add_command(build)
docs_cli.add_command(build_lang)
docs_cli.add_command(new_lang)
docs_cli.add_command(serve)
docs_cli.add_command(serve_lang)
docs_cli.add_command(dev)
docs_cli.add_command(verify_config)

if __name__ == "__main__":
    try:
        docs_cli()
    except DocsPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
