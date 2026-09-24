# Recomputerize writing agent skill

Install the Recomputerize writing skill through Claude Code, Codex, or Make.
The skill content is a placeholder:

> You are what you are.

Supports Linux and other Unix systems. Shared installation requires Python 3.10+
on PATH. No Python packages are needed to install or run the hook.

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

Start a new session with the plugin enabled. Its `SessionStart` hook runs the
shared installer. In Codex, review and trust the hook through `/hooks`, then start
another session. Installation alone does not grant hook trust.
[Codex plugin packaging](https://developers.openai.com/plugins/build/plugins),
[Codex hook trust](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks),
[Claude hooks](https://code.claude.com/docs/en/hooks#sessionstart).

Use `make install` below if hooks are unavailable or disabled, or to install the
shared skill immediately. A web-only marketplace installation cannot run this
local installer.

## Install with Make

Clone the repository and run the installer:

```sh
git clone https://github.com/cosgroveb/recomputerize-writing-agent-skill.git
cd recomputerize-writing-agent-skill
make install
```

The installer copies the skill and license to XDG user data storage and creates
two discovery links. With the default settings:

```text
~/.local/share/agents/skills/recomputerize-writing-agent-skill/
~/.agents/skills/recomputerize-writing-agent-skill -> shared copy
~/.claude/skills/recomputerize-writing-agent-skill -> shared copy
```

An absolute `XDG_DATA_HOME` replaces `~/.local/share`. An unset, empty, or relative
value uses the default. `CLAUDE_CONFIG_DIR` replaces `~/.claude` when set to an
absolute path. Installation is per user and needs no elevated privileges.
[XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/).

XDG defines this user layout. For administrator-managed, architecture-independent
data, FHS provides `/usr/local/share`. This installer configures user discovery,
so system-wide deployment remains an administrator task.
[FHS /usr/local](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html).

The shared copy survives removal of a marketplace cache. Repeated installs keep
unchanged files intact and replace the managed copy on updates. The installer
refuses unrelated files, directories, or symlinks at its destinations.
Edit the repository source, then reinstall.

Restart other agent sessions to discover the skill. Agents that scan
`~/.agents/skills` can use the shared copy. Discovery paths are a client
convention, separate from the portable skill format.
[Agent Skills discovery guidance](https://agentskills.io/client-implementation/adding-skills-support).

## Use

In Codex, invoke `$recomputerize-writing-agent-skill`. In Claude Code, use
`/recomputerize-writing-agent-skill:recomputerize-writing-agent-skill` for the
plugin, or `/recomputerize-writing-agent-skill` for the shared installation.

Installing both forms can expose both plugin and standalone entries in a
harness. They use the same authored skill.
[Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Claude skills](https://code.claude.com/docs/en/skills).

## Update or remove

Update the plugin through its marketplace, then start a new session. The hook
refreshes the shared copy. When the two marketplaces have different versions,
the hook preserves the newer shared version. From a checkout, `make install`
installs that checkout's version, including an intentional downgrade.

To remove everything, first uninstall the plugin from each harness where you
installed it. Then run this from a checkout:

```sh
make uninstall
```

Marketplace removal leaves the shared installation in place. An enabled plugin
will recreate it at the next matching session start. Uninstall refuses paths
that belong to another installation.

## Development

The repository holds one authored skill in
`skills/recomputerize-writing-agent-skill/SKILL.md`. Both marketplaces point at
the repository root. `plugin.json` supplies the portable Agent Plugins manifest.
`.claude-plugin/plugin.json` supplies Claude metadata. Both use
`hooks/hooks.json` and `scripts/install.py`.

Create a development environment and run the checks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
make check PYTHON=.venv/bin/python
```

`make check` validates metadata, marketplace paths, and skill frontmatter, then
tests installation in temporary directories. The checked-in
[Agent Plugins 1.0 schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
keeps schema validation offline. CI runs the same checks on Linux and macOS.
The skill follows the [Agent Skills format](https://agentskills.io/specification).

With Claude Code installed, also validate its marketplace, plugin, and skill:

```sh
claude plugin validate --strict .
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict skills
```

For isolated manual installation checks, pass explicit temporary paths:

```sh
python3 scripts/install.py install --home /tmp/recomputerize-user \
  --data-home /tmp/recomputerize-data \
  --claude-config /tmp/recomputerize-claude
```

Use the same paths with `uninstall` to remove that test installation.

## License

[Apache-2.0](LICENSE).
