#!/bin/bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
name=recomputerize-writing-agent-skill
repository="https://github.com/cosgroveb/$name"
receipt=.recomputerize-install.json
automatic=false
temporary=

die() { printf '%s: %s\n' "$name" "$*" >&2; exit 1; }
present() { [[ -e $1 || -L $1 ]]; }
absolute() { [[ $1 == /* ]] || die "Expected an absolute path: $1"; }
valid_version() { [[ $1 =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; }

newer() {
  local left right i
  IFS=. read -r -a left <<<"$1"
  IFS=. read -r -a right <<<"$2"
  for i in 0 1 2; do
    if [[ ${#left[i]} -ne ${#right[i]} ]]; then
      [[ ${#left[i]} -gt ${#right[i]} ]]
      return
    fi
    if [[ ${left[i]} != "${right[i]}" ]]; then
      [[ ${left[i]} > "${right[i]}" ]]
      return
    fi
  done
  return 1
}

mode() {
  case $platform in
    Darwin) stat -f '%Lp' "$1" ;;
    *) stat -c '%a' "$1" ;;
  esac
}

unchanged() {
  local file relative staged_mode installed_mode
  [[ -z $(find "$destination" -type l -print) ]] || return 1
  diff -qr "$temporary/skill" "$destination" >/dev/null || return 1
  while IFS= read -r -d '' file; do
    relative=${file#"$temporary/skill/"}
    [[ ! -L "$destination/$relative" ]] || return 1
    staged_mode=$(mode "$file") || return 1
    installed_mode=$(mode "$destination/$relative") || return 1
    [[ $staged_mode == "$installed_mode" ]] || return 1
  done < <(find "$temporary/skill" -type f -print0)
}

cleanup() {
  local status=$?
  trap - EXIT
  if [[ -n $temporary ]]; then
    if [[ -d "$temporary/previous" ]] && ! present "$destination"; then
      if ! mv "$temporary/previous" "$destination"; then
        printf 'Previous installation retained at %s\n' "$temporary/previous" >&2
        exit 1
      fi
    fi
    rm -rf "$temporary"
  fi
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

action=${1:-}
case $action in
  install|uninstall) shift ;;
  -h|--help)
    printf 'Usage: %s install|uninstall [--auto] [--home PATH] [--data-home PATH] [--claude-config PATH]\n' "$0"
    exit ;;
  *) die 'Expected install or uninstall' ;;
esac
user_root=${HOME:?HOME is required}
data_root=
claude_root=
while [[ $# -gt 0 ]]; do
  case $1 in
    --auto) automatic=true; shift ;;
    --home|--data-home|--claude-config)
      [[ $# -ge 2 ]] || die "Missing value for $1"
      absolute "$2"
      case $1 in
        --home) user_root=$2 ;;
        --data-home) data_root=$2 ;;
        --claude-config) claude_root=$2 ;;
      esac
      shift 2 ;;
    *) die "Unknown argument: $1" ;;
  esac
done
[[ $action == install || $automatic == false ]] || die '--auto applies only to install'
absolute "$user_root"
if [[ -z $data_root ]]; then
  case ${XDG_DATA_HOME:-} in
    /*) data_root=$XDG_DATA_HOME ;;
    *) data_root="$user_root/.local/share" ;;
  esac
fi
claude_root=${claude_root:-${CLAUDE_CONFIG_DIR:-"$user_root/.claude"}}
absolute "$claude_root"

destination="$data_root/agents/skills/$name"
links=("$user_root/.agents/skills/$name" "$claude_root/skills/$name")
# Resolve parents so aliases cannot make a discovery link replace the data.
parents=()
for path in "$destination" "${links[@]}"; do
  mkdir -p "${path%/*}"
  parents+=("$(cd "${path%/*}" && pwd -P)")
done
[[ ${parents[0]} != "${parents[1]}" && ${parents[0]} != "${parents[2]}" &&
   ${parents[1]} != "${parents[2]}" ]] || die 'Data and discovery directories must be distinct'

installed_version=
if present "$destination"; then
  [[ -d $destination && ! -L $destination && -f "$destination/$receipt" &&
     ! -L "$destination/$receipt" ]] || die "Refusing to replace an unmanaged path: $destination"
  # Keep accepting the two-field receipts from existing installations.
  record=$(<"$destination/$receipt")
  receipt_pattern='^[[:space:]]*\{[[:space:]]*"repository"[[:space:]]*:[[:space:]]*"([^"]*)"[[:space:]]*,[[:space:]]*"version"[[:space:]]*:[[:space:]]*"([^"]*)"[[:space:]]*\}[[:space:]]*$'
  [[ $record =~ $receipt_pattern ]] || die "Refusing an unrecognized install receipt: $destination/$receipt"
  [[ ${BASH_REMATCH[1]} == "$repository" ]] || die "Refusing an unrelated install: $destination"
  installed_version=${BASH_REMATCH[2]}
  valid_version "$installed_version" || die "Refusing invalid installed version: $installed_version"
fi
for link in "${links[@]}"; do
  if present "$link"; then
    [[ -L $link && $(readlink "$link") == "$destination" ]] || die "Refusing to replace an unrelated skill: $link"
  fi
done

if [[ $action == uninstall ]]; then
  for link in "${links[@]}"; do
    if [[ -L $link ]]; then rm "$link"; fi
  done
  if [[ -n $installed_version ]]; then rm -rf "$destination"; fi
  printf 'Removed %s\n' "$destination"
  exit
fi

# Package metadata uses one unescaped string field per line.
manifest_name=$(sed -n 's/^  "name": "\([^"]*\)",\{0,1\}$/\1/p' "$root/plugin.json")
[[ $manifest_name == "$name" ]] || die 'The plugin manifest and installer names disagree'
version=$(sed -n 's/^  "version": "\([^"]*\)",\{0,1\}$/\1/p' "$root/plugin.json")
valid_version "$version" || die "Expected a MAJOR.MINOR.PATCH version, got: $version"
source="$root/skills/$name"
[[ -f "$source/SKILL.md" ]] || die "Missing skill content: $source/SKILL.md"
platform=$(uname -s)

if [[ $automatic == false || -z $installed_version ]] || ! newer "$installed_version" "$version"; then
  temporary=$(mktemp -d "${destination%/*}/.$name.XXXXXX")
  cp -RLp "$source" "$temporary/skill"
  cp -p "$root/LICENSE" "$temporary/skill/LICENSE"
  printf '{\n  "repository": "%s",\n  "version": "%s"\n}\n' "$repository" "$version" \
    >"$temporary/skill/$receipt"
  if [[ -z $installed_version ]] || ! unchanged; then
    if [[ -n $installed_version ]]; then mv "$destination" "$temporary/previous"; fi
    mv "$temporary/skill" "$destination"
  fi
fi
for link in "${links[@]}"; do
  if [[ ! -L $link ]]; then ln -s "$destination" "$link"; fi
done
if [[ $automatic == false ]]; then printf 'Installed %s\n' "$destination"; fi
