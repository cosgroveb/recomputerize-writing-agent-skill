#!/usr/bin/env python3
"""Check the package metadata, marketplace entries, and skill frontmatter."""

import json
from pathlib import Path
import re
import sys

import jsonschema
import yaml

from install import NAME, REPOSITORY, version_parts


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check():
    plugin = read_json("plugin.json")
    schema = read_json("tests/schemas/plugin.schema.json")
    jsonschema.Draft202012Validator(schema).validate(plugin)
    require(plugin["name"] == NAME, "Plugin and installer names differ")
    require(plugin["repository"] == REPOSITORY, "Repository URL differs from installer")
    version_parts(plugin["version"])
    require(plugin["license"] == "Apache-2.0", "License metadata differs from LICENSE")
    require((ROOT / "LICENSE").is_file(), "Missing LICENSE")

    claude = read_json(".claude-plugin/plugin.json")
    shared_metadata = {
        key: value for key, value in plugin.items()
        if key not in ("$schema", "extensions")
    }
    require(claude == shared_metadata, "Claude and portable plugin metadata differ")

    for path in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        marketplace = read_json(path)
        require(marketplace["name"] == NAME, f"{path}: unexpected marketplace name")
        require(len(marketplace["plugins"]) == 1, f"{path}: expected one plugin")
        entry = marketplace["plugins"][0]
        require(entry["name"] == NAME, f"{path}: unexpected plugin name")
        require("version" not in entry, f"{path}: version belongs in plugin manifest")
        if path.startswith(".agents/"):
            require(
                entry["source"] == {"source": "local", "path": "./"},
                f"{path}: source must reference the repository root",
            )
            require(
                entry["policy"] == {
                    "installation": "AVAILABLE", "authentication": "ON_INSTALL"
                },
                f"{path}: unexpected installation policy",
            )
            require(entry["category"] == "Productivity", f"{path}: missing category")
        else:
            require(entry["source"] == "./", f"{path}: source must be ./")
            require(
                marketplace["owner"]["name"] == plugin["author"]["name"],
                f"{path}: publisher differs from plugin author",
            )

    skill_path = ROOT / "skills" / NAME / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8")
    require(skill.startswith("---\n"), "SKILL.md: missing YAML frontmatter")
    header, separator, body = skill[4:].partition("\n---\n")
    require(separator and body.strip(), "SKILL.md: missing frontmatter terminator or body")
    frontmatter = yaml.safe_load(header)
    require(isinstance(frontmatter, dict), "SKILL.md: frontmatter must be a mapping")
    name = frontmatter["name"]
    require(
        isinstance(name, str)
        and len(name) <= 64
        and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name),
        "SKILL.md: invalid Agent Skills name",
    )
    require(name == skill_path.parent.name == NAME, "SKILL.md: name differs from directory")
    description = frontmatter["description"]
    require(
        isinstance(description, str) and description.strip() and len(description) <= 1024,
        "SKILL.md: description must contain 1–1024 characters",
    )
    require(frontmatter["license"] == plugin["license"], "Skill and plugin licenses differ")

    extension = plugin["extensions"]["com.openai"]
    require(
        extension["hooks"] == "./hooks/hooks.json",
        "Codex and Claude must share the default hook file",
    )
    hooks = read_json("hooks/hooks.json")["hooks"]
    require(set(hooks) == {"SessionStart"}, "Expected only a SessionStart hook")
    require((ROOT / "scripts/install.py").is_file(), "Missing hook installer")
    print("Package metadata and skill frontmatter passed")


if __name__ == "__main__":
    try:
        check()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, jsonschema.ValidationError) as error:
        print(f"Package validation failed: {error}", file=sys.stderr)
        sys.exit(1)
