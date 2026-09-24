# Recomputerize writing agent skill

[![Check](https://github.com/cosgroveb/recomputerize-writing-agent-skill/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cosgroveb/recomputerize-writing-agent-skill/actions/workflows/ci.yml)

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

Run the four Bash integration tests:

```sh
make check
```

Each test copies the repository into a temporary directory and uses a synthetic
home. The tests cover installation, version changes, and preservation of
unmanaged installation and discovery paths. They require Bash and standard Unix
utilities, as does the installer. No package installation is required.

With Claude Code installed, also validate its marketplace, plugin, and skill:

```sh
claude plugin validate --strict .
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict skills
```

## License

[Apache-2.0](LICENSE).
