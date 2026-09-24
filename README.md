# Recomputerize writing agent skill

Install the Recomputerize writing skill through Claude Code, Codex, or Make.
The skill content is a placeholder:

> You are what you are.

## Install from GitHub

### Claude Code

```sh
claude plugin marketplace add cosgroveb/recomputerize-writing-agent-skill
claude plugin install recomputerize-writing-agent-skill@recomputerize-writing-agent-skill
```

### Codex

```sh
codex plugin marketplace add cosgroveb/recomputerize-writing-agent-skill
codex plugin add recomputerize-writing-agent-skill@recomputerize-writing-agent-skill
```

## Install with Make

`make install` installs to `$HOME/.agents/skills` on most systems.

Use it only for harnesses other than Claude or Codex, since it survives removal
of their marketplace caches.

```sh
git clone https://github.com/cosgroveb/recomputerize-writing-agent-skill.git
cd recomputerize-writing-agent-skill
make install
```

## Use

In Codex, invoke `$recomputerize-writing-agent-skill`. In Claude Code, use
`/recomputerize-writing-agent-skill:recomputerize-writing-agent-skill` for the
plugin, or `/recomputerize-writing-agent-skill` for a Make installation.

[Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Claude skills](https://code.claude.com/docs/en/skills).

## Remove

Uninstall the marketplace plugin through Claude or Codex, or remove the Make
installation with `make uninstall`.

## Development

Create a development environment and run the checks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
make check PYTHON=.venv/bin/python
```

`make check` validates metadata, marketplace paths, and skill frontmatter, then
tests installation in temporary directories.

With Claude Code installed, also validate its marketplace, plugin, and skill:

```sh
claude plugin validate --strict .
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict skills
```

## License

[Apache-2.0](LICENSE).
