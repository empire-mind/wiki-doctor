#!/usr/bin/env python3
"""Tests for wiki-doctor.py — every assertion verified by running it."""
import importlib.util as _ilu
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = _ilu.spec_from_file_location("wiki_doctor", HERE.parent / "wiki-doctor.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check = _mod.check

WD = HERE.parent / "wiki-doctor.py"


def wiki(tmp_path, files):
    for name, text in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return str(tmp_path)


def test_broken_link_detected(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[ghost]]"}))
    assert len(r["broken"]) == 1
    assert r["broken"][0][1] == "[[ghost]]"


def test_valid_link_clean(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[guide]]",
                              "guide.md": "hi"}))
    assert r["broken"] == []


def test_links_in_fences_ignored(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "```\n[[ghost]]\n```\n"}))
    assert r["broken"] == []


def test_links_in_inline_code_ignored(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "use `[[ghost]]` here"}))
    assert r["broken"] == []


def test_orphan_detected(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[guide]]",
                              "guide.md": "hi",
                              "scratch.md": "nobody links here"}))
    assert r["orphans"] == ["scratch.md"]


def test_index_exempt_from_orphans(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "home",
                              "guide.md": "see [[index]]"}))
    assert "index.md" not in r["orphans"]


def test_self_link_not_inbound(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[index]]"}))
    assert r["orphans"] == []


def test_stale_stamp_flagged(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "> Last synced: 2020-01-01\n"}))
    assert len(r["stale"]) == 1
    assert r["stale"][0][1] == "2020-01-01"


def test_fresh_stamp_not_flagged(tmp_path):
    import datetime
    today = datetime.date.today().isoformat()
    r = check(wiki(tmp_path, {"index.md": f"> Last synced: {today}\n"}))
    assert r["stale"] == []


def test_link_with_display_text(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[guide|the guide]]",
                              "guide.md": "hi"}))
    assert r["broken"] == []


def test_link_with_section(tmp_path):
    r = check(wiki(tmp_path, {"index.md": "see [[guide#setup]]",
                              "guide.md": "hi"}))
    assert r["broken"] == []


def test_cli_exit_codes(tmp_path):
    clean = wiki(tmp_path / "c", {"index.md": "hi"})
    dirty = wiki(tmp_path / "d", {"index.md": "see [[ghost]]"})
    ok = subprocess.run([sys.executable, str(WD), clean],
                        capture_output=True, text=True)
    bad = subprocess.run([sys.executable, str(WD), dirty],
                         capture_output=True, text=True)
    assert ok.returncode == 0 and "CLEAN" in ok.stdout
    assert bad.returncode == 1 and "BROKEN=1" in bad.stdout


def test_cli_json_shape(tmp_path):
    d = wiki(tmp_path, {"index.md": "see [[ghost]]"})
    out = subprocess.run([sys.executable, str(WD), "--json", d],
                         capture_output=True, text=True).stdout
    data = json.loads(out)
    assert data["broken"][0]["link"] == "[[ghost]]"
    assert data["files"] == 1


def test_demo_wiki_reports_all_three(tmp_path):
    import shutil
    demo = HERE.parent / "examples" / "my-wiki"
    dest = tmp_path / "demo"
    shutil.copytree(demo, dest)
    r = check(str(dest))
    assert len(r["broken"]) == 1
    assert r["orphans"] == ["old.md", "scratch.md"]
    assert len(r["stale"]) == 1
