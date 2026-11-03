# Copyright: (c) 2026, Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

"""``alai collection``: install, uninstall and list collections by hand, outside the project's requirements and lock."""

from __future__ import annotations

import argparse

from .._args import (
    HelpFormatter,
    add_global_args,
    add_reinstall_args,
    add_settings_args,
    add_upgrade_args,
    reinstall_from_args,
    settings_from_args,
    upgrade_from_args,
)


def register(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    collection = commands.add_parser(
        "collection",
        help="install, uninstall and list collections outside the project's requirements and alai.lock",
        description="Install, uninstall and list collections in the collections directory by hand, as uv pip does "
        + "for packages. Installing and uninstalling don't use or change the project's requirements or alai.lock, and "
        + "the next alai sync puts the collections directory back as the lock has it. When the project has an "
        + "alai.toml, its settings still apply, such as where collections are installed. Listing compares what's "
        + "installed with alai.lock.",
        formatter_class=HelpFormatter,
    )
    add_global_args(collection, suppress=True)
    collection.set_defaults(parser=collection)
    collection_commands = collection.add_subparsers(title="commands", metavar="<command>", prog="alai collection")

    install = collection_commands.add_parser(
        "install",
        help="install collections and what they need",
        description="Install collections and what they need into the collections directory, keeping installed "
        + "versions that fit. Nothing else is removed. Outside a project there's no collections directory to use, so "
        + "--collections-dir or the collections_dir setting has to say where.",
        formatter_class=HelpFormatter,
    )
    install.add_argument(
        "requirements",
        metavar="REQUIREMENT",
        nargs="*",
        help="a collection such as ansible.posix or 'cisco.ios>=11', a directory holding one such as ../ns.col, a "
        + "built collection's tarball by path or https:// URL, or a git repository given as "
        + "git+URL[@REV][#subdirectory=DIR&version=VERSION]. A directory is copied again every time",
    )
    install.add_argument(
        "-e",
        "--editable",
        metavar="DIR",
        action="append",
        default=[],
        help="install the source or built collection in DIR as a link to it, so edits there are seen "
        + "(can be repeated)",
    )
    add_upgrade_args(install)
    add_reinstall_args(install)
    install.add_argument(
        "--keep-unversioned",
        action="store_true",
        help="treat an installed collection whose version can't be read as the version asked for, rather than "
        + "replace it, such as a source checkout with no MANIFEST.json",
    )
    add_global_args(install, suppress=True)
    add_settings_args(install, "resolve", "install")
    install.set_defaults(parser=install, handler=run_install)

    uninstall = collection_commands.add_parser(
        "uninstall",
        help="uninstall collections",
        description="Uninstall collections from the collections directory. What they depend on stays. A collection is "
        + "given by its name, even one installed from a directory, a tarball or a git repository. Outside a project "
        + "there's no collections directory to use, so --collections-dir or the collections_dir setting has to say "
        + "where.",
        formatter_class=HelpFormatter,
    )
    uninstall.add_argument(
        "names",
        metavar="NAME",
        nargs="+",
        help="a collection name, such as ansible.posix, not the directory, tarball or git URL it was installed from",
    )
    add_global_args(uninstall, suppress=True)
    add_settings_args(uninstall, "install")
    uninstall.set_defaults(parser=uninstall, handler=run_uninstall)

    list_ = collection_commands.add_parser(
        "list",
        help="list the installed collections",
        description="List the collections in the collections directory, whatever installed them. When the project "
        + "has an alai.lock, each is shown as locked, not in it, installed differently, or locked but not installed. "
        + "Outside a project there's no collections directory to use, so --collections-dir or the collections_dir "
        + "setting has to say where.",
        formatter_class=HelpFormatter,
    )
    list_.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="text, the default, or json for scripts",
    )
    add_global_args(list_, suppress=True)
    add_settings_args(list_, "collections_dir")
    list_.set_defaults(parser=list_, handler=run_list)

    path = collection_commands.add_parser(
        "path",
        help="show where a collection's files are on disk",
        description="Show where each collection's files are on disk, for tools that read them such as a "
        + "documentation viewer. alai uses the first copy it finds, checking in order the collection project's own "
        + "checkout, the collections directory, the version in alai.lock and the newest version in the cache. "
        + "If none of them has the collection, alai downloads the latest version from the indexes into the cache. "
        + "The files for ansible.builtin and eda.builtin come from the latest ansible-core or ansible-rulebook "
        + "release on the Python index. "
        + "With --output-format json, NAME can be left out to show only the project's own collection.",
        formatter_class=HelpFormatter,
    )
    _ = path.add_argument("names", metavar="NAME", nargs="*", help="a collection, such as community.general")
    _ = path.add_argument(
        "--no-download",
        action="store_true",
        help="only use what's already on disk, without downloading anything or checking the indexes for a newer "
        + "version",
    )
    _ = path.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="text, the default, or json for scripts",
    )
    add_global_args(path, suppress=True)
    add_settings_args(path, "resolve", "collections_dir")
    path.set_defaults(parser=path, handler=run_path)


def run_install(args: argparse.Namespace) -> int:
    from .._collection import install

    if not args.requirements and not args.editable:
        args.parser.error("the following arguments are required: REQUIREMENT or --editable")
    reinstall = reinstall_from_args(args)
    if reinstall and args.keep_unversioned:
        # Keeping a collection as it is and reinstalling it ask for opposite things.
        args.parser.error("--keep-unversioned can't be used with --reinstall or --reinstall-collection")
    install(
        settings_from_args(args),
        args.requirements,
        upgrade=upgrade_from_args(args).names(None),
        reinstall=reinstall,
        keep_unversioned=args.keep_unversioned,
        editable=args.editable,
    )
    return 0


def run_uninstall(args: argparse.Namespace) -> int:
    from .._collection import uninstall

    uninstall(settings_from_args(args), args.names)
    return 0


def run_list(args: argparse.Namespace) -> int:
    from .._list import list_collections

    list_collections(settings_from_args(args), output_format=args.output_format)
    return 0


def run_path(args: argparse.Namespace) -> int:
    from .._locate import collection_path

    if not args.names and args.output_format == "text":
        args.parser.error("the following arguments are required: NAME")
    return collection_path(
        settings_from_args(args), args.names, download=not args.no_download, output_format=args.output_format
    )
