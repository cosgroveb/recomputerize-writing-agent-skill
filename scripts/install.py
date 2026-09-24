#!/usr/bin/env python3
"""Install the shared skill and its user discovery links on Unix."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
NAME = "recomputerize-writing-agent-skill"
REPOSITORY = f"https://github.com/cosgroveb/{NAME}"
RECEIPT = ".recomputerize-install.json"


def version_parts(version):
    if not isinstance(version, str) or not re.fullmatch(
        r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version
    ):
        raise ValueError(f"Expected a MAJOR.MINOR.PATCH version, got {version!r}")
    return tuple(int(part) for part in version.split("."))


def present(path):
    return path.exists() or path.is_symlink()


@contextmanager
def locked_directory(directory):
    directory.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        # Directory locks need no persistent lock file or stale-lock recovery.
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def managed_version(destination):
    if not present(destination):
        return None
    receipt_path = destination / RECEIPT
    if (
        destination.is_symlink()
        or not destination.is_dir()
        or receipt_path.is_symlink()
        or not receipt_path.is_file()
    ):
        raise ValueError(f"Refusing to replace an unmanaged path: {destination}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict) or receipt.get("repository") != REPOSITORY:
        raise ValueError(f"Refusing an unrecognized install receipt: {receipt_path}")
    version = receipt["version"]
    version_parts(version)
    return version


def check_links(links, destination):
    for link in links:
        if present(link) and (
            not link.is_symlink() or link.readlink() != destination
        ):
            raise ValueError(f"Refusing to replace an unrelated skill: {link}")


def tree_state(directory):
    entries = {}
    for path in directory.rglob("*"):
        relative = str(path.relative_to(directory))
        if path.is_symlink():
            entries[relative] = ("symlink", str(path.readlink()))
        elif path.is_dir():
            entries[relative] = ("directory",)
        else:
            entries[relative] = (
                stat.S_IMODE(path.stat().st_mode),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
    return entries


def install(destination, links, installed_version, automatic):
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    if manifest["name"] != NAME:
        raise ValueError("The plugin manifest and installer names disagree")
    version = manifest["version"]
    version_parts(version)
    source = ROOT / "skills" / NAME
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"Missing skill content: {source / 'SKILL.md'}")

    # A second harness may still have an older marketplace version cached.
    update = not (
        automatic
        and installed_version is not None
        and version_parts(installed_version) > version_parts(version)
    )
    if update:
        temporary = Path(tempfile.mkdtemp(prefix=f".{NAME}-", dir=destination.parent))
        staging = temporary / "skill"
        previous = temporary / "previous"
        activated = False
        try:
            shutil.copytree(source, staging)
            shutil.copy2(ROOT / "LICENSE", staging / "LICENSE")
            receipt = {"repository": REPOSITORY, "version": version}
            (staging / RECEIPT).write_text(
                json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
            )
            if installed_version is None or tree_state(staging) != tree_state(destination):
                try:
                    if installed_version is not None:
                        destination.rename(previous)
                    staging.rename(destination)
                    activated = True
                finally:
                    if not activated and previous.exists():
                        previous.rename(destination)
        finally:
            if activated or not previous.exists():
                shutil.rmtree(temporary)
            else:
                print(f"Previous installation retained at {previous}", file=sys.stderr)

    for link in links:
        if not link.is_symlink():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(destination, target_is_directory=True)


def uninstall(destination, links, installed_version):
    for link in links:
        if link.is_symlink():
            link.unlink()
    if installed_version is not None:
        shutil.rmtree(destination)


def absolute_path(value):
    path = Path(value)
    if not path.is_absolute():
        raise argparse.ArgumentTypeError(f"Expected an absolute path: {value}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument(
        "--auto", action="store_true",
        help="Install silently and preserve newer versions installed by another harness",
    )
    parser.add_argument("--home", type=absolute_path, default=Path.home())
    parser.add_argument("--data-home", type=absolute_path)
    parser.add_argument("--claude-config", type=absolute_path)
    args = parser.parse_args()
    if args.auto and args.action != "install":
        parser.error("--auto applies only to install")

    # XDG requires clients to ignore relative paths, including an empty value.
    xdg_data = Path(os.environ.get("XDG_DATA_HOME", ""))
    data_root = args.data_home or (
        xdg_data if xdg_data.is_absolute() else args.home / ".local/share"
    )
    claude_config = os.environ.get("CLAUDE_CONFIG_DIR")
    claude_root = args.claude_config or (
        absolute_path(claude_config) if claude_config else args.home / ".claude"
    )
    destination = data_root / "agents/skills" / NAME
    links = (args.home / ".agents/skills" / NAME, claude_root / "skills" / NAME)
    paths = (destination, *links)
    if len({path.parent.resolve() / path.name for path in paths}) != len(paths):
        raise ValueError("Data and discovery directories must be distinct")

    with locked_directory(destination.parent):
        installed_version = managed_version(destination)
        check_links(links, destination)
        if args.action == "install":
            install(destination, links, installed_version, args.auto)
        else:
            uninstall(destination, links, installed_version)
    if not args.auto:
        verb = "Installed" if args.action == "install" else "Removed"
        print(f"{verb} {destination}")


if __name__ == "__main__":
    # Let hook timeouts unwind the replacement before the process exits.
    def terminate(signum, frame):
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, terminate)
    try:
        main()
    except (OSError, ValueError, KeyError, argparse.ArgumentTypeError) as error:
        print(f"{NAME}: {error}", file=sys.stderr)
        sys.exit(1)
