# Copyright: (c) 2026, Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

"""The fixture for the docs' terminal recordings in ``docs/recordings.toml``, loaded by ``python -m cli_recorder``.

The recordings run against a local index built as the tests build one, served with a delay so the progress shows as
it would over a network. Only a version with a ``download`` checksum reaches the network, for its real artifact.
"""

from __future__ import annotations

import collections.abc as _c
import contextlib
import hashlib
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, "tests")

from artifact_data import build_artifact
from index_data import make_index, v
from index_server import IndexServer
from python_index import make_python_index

DOWNLOADS = "https://dl.alai.sh/sha256/{prefix}/{cksum}.tar.gz"
"""Where a version with a ``download`` checksum in ``[index]`` is fetched from: the real artifact, for a recording that
runs Ansible against it."""

# Seconds the index takes to answer, so the progress shows as it would over a network. Downloads take longest.
INDEX_DELAY = 0.15
DOWNLOAD_DELAY = 0.4


@contextlib.contextmanager
def environment(root: pathlib.Path, scenarios: dict[str, object]) -> _c.Generator[dict[str, str]]:
    """Serve ``[index]`` and ``plugins`` as alai's default index, and ansible-core's and ansible-rulebook's sdists, for
    ansible.builtin and eda.builtin, as its Python index."""
    index = _as_dict(scenarios.get("index"))
    collections = {name: [_version(s, root) for s in _as_dicts(versions)] for name, versions in index.items()}
    plugins = [{"v": 1, **line} for line in _as_dicts(scenarios.get("plugins"))]
    _ = make_index(root / "index", collections, artifacts=True, plugins=plugins)
    make_python_index(root / "index" / "pypi", plugins)
    with IndexServer(root / "index") as server:
        # The index points at its artifacts as file:// URLs; served over HTTP, they take time as downloads do.
        config = root / "index" / "config.json"
        settings = json.loads(config.read_text())
        settings["dl"] = server.url + "dl/{sha256-checksum}.tar.gz"
        _ = config.write_text(json.dumps(settings))
        server.delay = INDEX_DELAY
        server.delays = {f"/dl/{p.name}": DOWNLOAD_DELAY for p in (root / "index" / "dl").iterdir()}
        yield {"ALAI_DEFAULT_INDEX": server.url, "ALAI_PYTHON_INDEX": f"{server.url}pypi/"}


def prepare(recording: dict[str, object], directory: pathlib.Path) -> None:
    """Build each of a recording's ``tarballs`` at its path in ``directory``."""
    for path, spec in _as_dict(recording.get("tarballs")).items():
        _tarball(directory / path, _as_dict(spec))


def _version(spec: dict[str, object], root: pathlib.Path) -> dict[str, object]:
    """An ``[index]`` version for ``make_index``: one with a ``download`` checksum gets that real artifact, fetched and
    checked against it, in place of one holding only a README."""
    version = v(str(spec["vers"]), spec.get("deps"))  # pyright: ignore[reportArgumentType]
    cksum = spec.get("download")
    if isinstance(cksum, str):
        url = DOWNLOADS.format(prefix=cksum[:2], cksum=cksum)
        # Named, as the artifact store refuses urllib's default User-Agent.
        request = urllib.request.Request(url, headers={"User-Agent": "alai-docs-recordings"})  # noqa: S310 - a fixed https URL
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - a fixed https URL
            data: bytes = response.read()
        if hashlib.sha256(data).hexdigest() != cksum:
            msg = f"{url} doesn't match its sha256 {cksum}"
            raise RuntimeError(msg)
        tarball = root / f"{cksum}.tar.gz"
        _ = tarball.write_bytes(data)
        version["tarball"] = tarball
    return version


def _tarball(path: pathlib.Path, spec: dict[str, object]) -> None:
    """A built collection's tarball at ``path``, as ``ansible-galaxy collection build`` lays one out: ``name``,
    ``version``, ``dependencies`` for its ``MANIFEST.json``, and ``files``, its other files by relative path."""
    name, version = str(spec["name"]), str(spec["version"])
    namespace, short = name.split(".")
    files: dict[str, bytes | object] = {p: str(c).lstrip("\n").encode() for p, c in _as_dict(spec.get("files")).items()}
    info = {
        "namespace": namespace,
        "name": short,
        "version": version,
        "dependencies": _as_dict(spec.get("dependencies")),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = build_artifact(path, name, version, files, manifest={"collection_info": info})  # pyright: ignore[reportArgumentType]


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}  # pyright: ignore[reportUnknownVariableType]


def _as_dicts(value: object) -> list[dict[str, object]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []  # pyright: ignore[reportUnknownVariableType]
