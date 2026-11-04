"""Checks every skill's SKILL.md against the rules of Claude.ai and the Skills API, the plugin and marketplace files,
and runs the pdfpecker skill's script on its templates."""
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLUGINS = os.path.join(ROOT, "plugins")
SKILL = os.path.join(PLUGINS, "pdfpecker", "skills", "pdfpecker")
SCRIPT = os.path.join(SKILL, "scripts", "pdf.py")
# Claude.ai, the Skills API and the skill packager accept only these keys; Claude Code accepts more, but a skill that
# uses them cannot be uploaded.
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def skill_dirs():
    for plugin in sorted(os.listdir(PLUGINS)):
        skills = os.path.join(PLUGINS, plugin, "skills")
        for name in sorted(os.listdir(skills)):
            yield os.path.join(skills, name)


def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path} has no frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        if line and not line[0].isspace():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields, text[match.end():]


@pytest.mark.parametrize("skill", list(skill_dirs()), ids=os.path.basename)
def test_skill_frontmatter(skill):
    fields, body = frontmatter(os.path.join(skill, "SKILL.md"))
    assert set(fields) <= ALLOWED_KEYS, f"keys not allowed on Claude.ai: {set(fields) - ALLOWED_KEYS}"
    name = fields["name"]
    assert name == os.path.basename(skill)
    assert re.fullmatch(r"[a-z0-9-]{1,64}", name) and "claude" not in name and "anthropic" not in name
    description = fields["description"]
    assert 0 < len(description) <= 1024 and "<" not in description
    assert len(fields.get("compatibility", "")) <= 500
    assert len(body.splitlines()) < 500
    for link in re.findall(r"\]\(([^)#:]+)\)", body):
        assert os.path.exists(os.path.join(skill, link)), f"broken link {link}"


def test_marketplace_and_plugins():
    with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
        market = json.load(f)
    assert market["name"] and market["owner"]["name"]
    for entry in market["plugins"]:
        assert entry["source"].startswith("./")
        plugin_dir = os.path.join(ROOT, entry["source"])
        with open(os.path.join(plugin_dir, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            plugin = json.load(f)
        assert plugin["name"] == entry["name"]
        assert plugin["version"] == entry["version"]
        assert os.path.isdir(os.path.join(plugin_dir, "skills"))


def run(*args, cwd):
    result = subprocess.run([sys.executable, SCRIPT, *args], cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_templates_convert(tmp_path):
    for name in ("invoice", "report"):
        src = os.path.join(SKILL, "templates", f"{name}.html")
        code, out, err = run("html", src, str(tmp_path / f"{name}.pdf"), "--fixed-date", cwd=tmp_path)
        assert code == 0, err
    code, out, _ = run("info", "invoice.pdf", cwd=tmp_path)
    assert "1 page(s)" in out
    code, out, _ = run("info", "report.pdf", cwd=tmp_path)
    assert "4 page(s)" in out
    # The contents list has page numbers, and the cover has no running header.
    code, out, _ = run("text", "report.pdf", "--pages", "2", cwd=tmp_path)
    assert re.search(r"Summary\s+2", out) and re.search(r"Order details\s+4", out)
    code, out, _ = run("text", "report.pdf", "--pages", "1", cwd=tmp_path)
    assert "Quarterly Report" in out and "/ 4" not in out


def test_preview_markdown_and_merge(tmp_path):
    (tmp_path / "notes.md").write_text("# Notes\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n- [x] done\n", encoding="utf-8")
    code, _, err = run("md", "notes.md", "notes.pdf", "--page-size", "100x150", "--footer", "Page {page} of {pages}",
                       cwd=tmp_path)
    assert code == 0, err
    code, out, err = run("preview", "notes.pdf", "--dpi", "40", "--out-dir", "png", cwd=tmp_path)
    assert code == 0, err
    paths = out.split()
    assert paths and all((tmp_path / p).exists() and p.endswith(".png") for p in paths)
    code, out, err = run("merge", "both.pdf", "notes.pdf", "notes.pdf", cwd=tmp_path)
    assert code == 0, err
    assert f"{2 * len(paths)} page(s)" in out


def test_errors_exit_with_one(tmp_path):
    code, _, err = run("text", "missing.pdf", cwd=tmp_path)
    assert code == 1 and "error" in err
    (tmp_path / "a.html").write_text("<p>x", encoding="utf-8")
    code, _, err = run("html", "a.html", "a.pdf", "--page-size", "B9", cwd=tmp_path)
    assert code == 1 and "page_size" in err
    code, _, _ = run("html", cwd=tmp_path)
    assert code == 2
