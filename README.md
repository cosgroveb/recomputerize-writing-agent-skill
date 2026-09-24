# Recomputerize writing agent skill

[![Check](https://github.com/cosgroveb/recomputerize-writing-agent-skill/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cosgroveb/recomputerize-writing-agent-skill/actions/workflows/ci.yml)

Recomputerize removes unnecessary anthropomorphization of writing about LLMs
while preserving meaning, technical terms, and the writer's voice.

> De-anthropomorphizing language talks about computer systems in terms of their
> functionality (what people build and/or use them to do), assigns agency to people
> using systems and not systems, and avoids aggrandizing metaphors about cognition.

Emily M. Bender and Nanna Inie,
[How to talk about “AI” without adding to the anthropomorphization](https://buttondown.com/maiht3k/archive/how-to-talk-about-ai-without-adding-to-the/).

Install it through Claude Code, Codex, or Make.

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

Run the Bash integration tests:

```sh
make check
```

With Claude Code installed, also validate its marketplace, plugin, and skill:

```sh
claude plugin validate --strict .
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict skills
```

## License

[Apache-2.0](LICENSE).
