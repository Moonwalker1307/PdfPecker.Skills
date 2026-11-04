# AGENTS.md

Guidance for coding agents (and people) working in this repository. `CLAUDE.md` imports this file, so Claude Code and
other agents read the same rules.

PdfPecker.Skills holds Agent Skills that use [PdfPecker](https://github.com/Moonwalker1307/PdfPecker) through the
[pdfpecker](https://pypi.org/project/pdfpecker/) Python package (repository Moonwalker1307/PdfPecker.Python), packaged
as a Claude Code plugin marketplace. The same skill folders are zipped for Claude.ai and the Skills API.

## Core rules

- **Skills describe the released package.** Every option, CSS feature and behaviour a skill names must work with the
  pdfpecker version on PyPI; try it before writing it down. A feature that is only on the library's `main` waits
  for the release.
- **Portable frontmatter.** SKILL.md uses only `name`, `description`, `license`, `compatibility`, `metadata` and
  `allowed-tools`, which Claude.ai and the Skills API accept; Claude Code-only keys and `${CLAUDE_SKILL_DIR}`
  substitutions in commands would break the upload. `name` is lowercase with hyphens, at most 64 characters, and
  matches the folder; `description` is at most 1,024 characters and says when to use the skill.
- **Scripts use only the standard library and pdfpecker**, run on Python 3.9+, on Linux, macOS and Windows, and exit
  0 on success, 1 when the work failed (with the reason on stderr) and 2 for a wrong command line.
- **Plugin versions move together.** A change to a plugin bumps `version` in its `plugin.json` and its
  `marketplace.json` entry, so installed copies update.
- **Never name a user's private application or employer** in skills, templates, tests, commits or PR descriptions.
  Templates use neutral names such as "Example Customer Ltd.".

## Repo map

- `.claude-plugin/marketplace.json` – the marketplace (`pdfpecker-skills`) and its plugins.
- `plugins/pdfpecker/` – the plugin: `.claude-plugin/plugin.json` and `skills/pdfpecker/` (`SKILL.md`, `reference.md`,
  `scripts/pdf.py`, `templates/`).
- `tests/test_skills.py` – frontmatter, manifest and link checks, and end-to-end runs of the scripts.
- `tools/package.py` – zips each skill folder; CI attaches the zips to each release.

## Build and verify

```
python -m pip install pdfpecker pytest
python -m pytest -q tests
python tools/package.py          # dist/<skill>.zip
```

Look at the PDFs the templates make (`scripts/pdf.py preview`) after changing a template.

## Commit guidance

- Branch from the latest `origin/main`, one branch per piece of work, named after the work with a `claude/` prefix
  when an agent creates it. Never reuse a branch name after its PR is merged or closed.
- Commit subjects are short imperative or descriptive sentences without prefixes; the body explains why.
- Fill in `.github/pull_request_template.md`, and update `README.md` when a skill, command or install step changes.
- Releases (which attach the skill zips) are the owner's step.
