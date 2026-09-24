#!/bin/bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
name=recomputerize-writing-agent-skill

fail() {
  printf 'FAIL: %s: %s\n' "$scenario" "$*" >&2
  exit 1
}

installer() {
  bash "$package/scripts/install.sh" "$@" --home "$user_root" \
    >"$work/stdout" 2>"$work/stderr"
}

install_skill() {
  installer install "$@" || { cat "$work/stderr" >&2; fail 'install failed'; }
}

refuse() {
  if installer "$@"; then fail 'accepted an unmanaged path'; fi
  grep -q Refusing "$work/stderr" || fail 'missing refusal diagnostic'
}

assert_installed() {
  [[ $(readlink "$agent_link") == "$destination" ]] || fail 'agent link'
  [[ $(readlink "$claude_link") == "$destination" ]] || fail 'Claude link'
  cmp "$agent_link/SKILL.md" "$source/SKILL.md"
  cmp "$destination/LICENSE" "$package/LICENSE"
}

change_package() {
  sed "s/\"version\": \"[^\"]*\"/\"version\": \"$1\"/" \
    "$package/plugin.json" >"$work/manifest"
  mv "$work/manifest" "$package/plugin.json"
  printf '%s\n' "$2" >"$source/SKILL.md"
}

installation_lifecycle() {
  install_skill
  assert_installed
  ln "$destination/SKILL.md" "$work/original"
  cp -p "$destination/SKILL.md" "$work/timestamp"
  install_skill
  [[ "$destination/SKILL.md" -ef "$work/original" ]] || fail 'replaced unchanged file'
  [[ ! "$destination/SKILL.md" -nt "$work/timestamp" &&
     ! "$work/timestamp" -nt "$destination/SKILL.md" ]] || fail 'changed timestamp'
  mv "$package" "$work/relocated plugin"
  package="$work/relocated plugin"
  source="$package/skills/$name"
  assert_installed
  neighbor="${destination%/*}/another-skill"
  mkdir "$neighbor"
  printf 'keep\n' >"$neighbor/SKILL.md"
  installer uninstall
  installer uninstall
  [[ ! -e "$destination" && ! -L "$destination" ]] || fail 'installation remains'
  [[ ! -e "$agent_link" && ! -L "$agent_link" ]] || fail 'agent link remains'
  [[ ! -e "$claude_link" && ! -L "$claude_link" ]] || fail 'Claude link remains'
  [[ $(<"$neighbor/SKILL.md") == keep ]] || fail 'neighbor changed'
}

version_changes() {
  printf 'obsolete\n' >"$source/old.txt"
  install_skill
  rm "$source/old.txt"
  printf '#!/bin/sh\nexit 0\n' >"$source/example.sh"
  chmod 755 "$source/example.sh"
  change_package 0.2.0 'Updated skill.'
  install_skill --auto
  assert_installed
  [[ ! -e "$destination/old.txt" ]] || fail 'obsolete file remains'
  case $(uname -s) in
    Darwin) mode=$(stat -f '%Lp' "$destination/example.sh") ;;
    *) mode=$(stat -c '%a' "$destination/example.sh") ;;
  esac
  [[ $mode == 755 ]] || fail 'executable mode changed'
  change_package 0.1.0 'Older content.'
  rm "$claude_link"
  install_skill --auto
  [[ $(<"$destination/SKILL.md") == 'Updated skill.' ]] || fail 'automatic downgrade'
  [[ $(readlink "$claude_link") == "$destination" ]] || fail 'missing repaired link'
  install_skill
  assert_installed
}

unmanaged_destination() {
  mkdir -p "$destination" "$work/foreign"
  printf 'keep\n' >"$destination/mine.txt"
  refuse install
  [[ $(<"$destination/mine.txt") == keep ]] || fail 'unmanaged content changed'
  [[ ! -L "$agent_link" ]] || fail 'created discovery link'
  refuse uninstall
  [[ $(<"$destination/mine.txt") == keep ]] || fail 'unmanaged content removed'
  rm "$destination/mine.txt"
  rmdir "$destination"
  ln -s "$work/foreign" "$destination"
  refuse install
  [[ $(readlink "$destination") == "$work/foreign" ]] || fail 'replaced canonical symlink'
  [[ -z $(ls -A "$work/foreign") ]] || fail 'modified symlink target'
}

discovery_conflicts() {
  mkdir -p "${claude_link%/*}" "$work/foreign"
  printf 'keep\n' >"$work/foreign/keep.txt"
  for kind in directory file symlink broken-symlink; do
    case $kind in
      directory) mkdir "$claude_link" ;;
      file) printf 'keep\n' >"$claude_link" ;;
      symlink) ln -s "$work/foreign" "$claude_link" ;;
      broken-symlink) ln -s "$work/missing" "$claude_link" ;;
    esac
    refuse install
    [[ ! -e "$destination" ]] || fail "$kind: created installation"
    [[ ! -L "$agent_link" ]] || fail "$kind: created agent link"
    [[ $(<"$work/foreign/keep.txt") == keep ]] || fail "$kind: changed foreign content"
    if [[ $kind == directory ]]; then rmdir "$claude_link"; else rm "$claude_link"; fi
  done
  install_skill
  cp "$destination/SKILL.md" "$work/previous"
  rm "$claude_link"
  printf 'keep\n' >"$claude_link"
  change_package 0.2.0 replacement
  refuse install
  refuse uninstall
  cmp "$destination/SKILL.md" "$work/previous"
  [[ $(<"$claude_link") == keep ]] || fail 'conflicting file changed'
  [[ -L "$agent_link" ]] || fail 'agent link removed'
}

if [[ $# == 1 ]]; then
  scenario=$1
  work=$(mktemp -d /tmp/recomputerize-test.XXXXXX)
  trap 'rm -rf "$work"' EXIT
  package="$work/plugin \$ ' copy"
  mkdir "$package"
  tar -C "$root" --exclude=.git -cf - . | tar -C "$package" -xf -
  user_root="$work/user"
  destination="$user_root/.local/share/agents/skills/$name"
  agent_link="$user_root/.agents/skills/$name"
  claude_link="$user_root/.claude/skills/$name"
  source="$package/skills/$name"
  unset XDG_DATA_HOME CLAUDE_CONFIG_DIR
  cd "$work"
  case $scenario in
    installation_lifecycle) installation_lifecycle ;;
    version_changes) version_changes ;;
    unmanaged_destination) unmanaged_destination ;;
    discovery_conflicts) discovery_conflicts ;;
    *) fail 'unknown scenario' ;;
  esac
  exit
fi

failed=0
for scenario in installation_lifecycle version_changes unmanaged_destination discovery_conflicts; do
  if bash "$0" "$scenario"; then
    printf 'PASS: %s\n' "$scenario"
  else
    printf 'FAIL: %s\n' "$scenario" >&2
    failed=1
  fi
done
exit "$failed"
