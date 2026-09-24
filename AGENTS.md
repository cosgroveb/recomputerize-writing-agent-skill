# Repository conventions

The skill content is intentionally a placeholder. Develop its writing
instructions only when requested.

- Author content in `skills/recomputerize-writing-agent-skill/`. Add supporting
  resources there when the content needs them.
- Keep one copy of the authored skill. Both marketplaces load the repository
  root. No generated distribution tree is needed.
- Keep shared metadata identical in `plugin.json` and
  `.claude-plugin/plugin.json`. Use `MAJOR.MINOR.PATCH` release versions and bump
  both manifests together. Marketplace entries inherit the plugin version.
- Keep installation code in `scripts/install.sh`. Use Bash and standard Unix
  utilities without additional packages. Both the hook and Make call this installer.
- Preserve the separation between XDG data storage and harness discovery links.
  Refuse unrelated installation paths. Automatic hooks must preserve newer
  installed versions and produce no context on stdout.
- Run `make check` for the four Bash integration tests. No test framework or
  development packages are required.
- Exercise installers in temporary directories with `--home`, `--data-home`,
  and `--claude-config`. Do not use personal harness installations as test fixtures.

Check the current harness documentation before changing packaging or hook behavior.
