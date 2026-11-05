# Copyright: (c) 2026, Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from alai._common import WORKDIR_PREFIX, cache_workdir, manifest_info, rename_into_cache


class TestCacheWorkdir:
    def test_makes_the_root(self, tmp_path: Path) -> None:
        work = cache_workdir(str(tmp_path / "cache" / "layout"))

        assert Path(work).is_dir()
        assert Path(work).name.startswith(WORKDIR_PREFIX)

    def test_removes_stale_workdirs_only(self, tmp_path: Path) -> None:
        stale = tmp_path / f"{WORKDIR_PREFIX}old"
        stale.mkdir()
        _ = (stale / "partial").write_text("x")
        day_ago = time.time() - 25 * 60 * 60
        os.utime(stale, (day_ago, day_ago))
        fresh = tmp_path / f"{WORKDIR_PREFIX}live"
        fresh.mkdir()
        kept = tmp_path / "abc123"
        kept.mkdir()
        os.utime(kept, (day_ago, day_ago))

        work = cache_workdir(str(tmp_path))

        assert sorted(p.name for p in tmp_path.iterdir()) == sorted([Path(work).name, fresh.name, kept.name])


class TestRenameIntoCache:
    def test_moves(self, tmp_path: Path) -> None:
        (tmp_path / "work").mkdir()

        rename_into_cache(str(tmp_path / "work"), str(tmp_path / "target"))

        assert (tmp_path / "target").is_dir()

    def test_keeps_another_runs_copy(self, tmp_path: Path) -> None:
        (tmp_path / "work").mkdir()
        (tmp_path / "target").mkdir()
        _ = (tmp_path / "target" / "theirs").write_text("")

        rename_into_cache(str(tmp_path / "work"), str(tmp_path / "target"))

        assert (tmp_path / "target" / "theirs").is_file()

    def test_other_errors_raise(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            rename_into_cache(str(tmp_path / "missing"), str(tmp_path / "target"))


class TestManifestInfo:
    def test_reads(self, tmp_path: Path) -> None:
        _ = (tmp_path / "MANIFEST.json").write_text(
            '{"collection_info": {"namespace": "ns", "name": "col", "version": "1.2.3"}}'
        )

        info = manifest_info(str(tmp_path / "MANIFEST.json"))

        assert info is not None
        assert (info[0], info[1].text) == ("ns.col", "1.2.3")

    @pytest.mark.parametrize("content", ["", "{}", '{"collection_info": {"version": "1"}}', '{"collection_info": 1}'])
    def test_unreadable(self, tmp_path: Path, content: str) -> None:
        _ = (tmp_path / "MANIFEST.json").write_text(content)

        assert manifest_info(str(tmp_path / "MANIFEST.json")) is None
        assert manifest_info(str(tmp_path / "missing.json")) is None
