#!/usr/bin/env python3
"""Print the Origin webhook payload families with their fields resolved.

Usage:
    python3 index-origin-spec.py openapi.yaml                  # every payload family
    python3 index-origin-spec.py openapi.yaml schema PullRequest   # one component

Fetch the spec first:
    curl -sSL https://cursor.com/docs/api/origin/openapi.yaml -o openapi.yaml

Operations and scopes do not need this script. Grep the spec directly:
    rg -B1 -A4 'x-origin-scopes:' openapi.yaml
    rg -A3 'x-origin-webhook-events:' openapi.yaml

Read-only. Needs PyYAML (`pip install pyyaml`). Everything printed comes from
the spec you pass in; nothing is pinned or embedded here.
"""

import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "PyYAML is not installed. Run `pip install pyyaml`, or read the spec "
        "directly (search for `x-origin-webhook-events:` and follow the "
        "`$ref`s by hand).\n"
    )
    sys.exit(2)

# Field descriptions are cut to one sentence and this many characters so a
# family fits on one screen.
DESCRIPTION_CHARS = 140
# How many `$ref` levels to expand under a payload. Two reaches the embedded
# resource and its direct children, which is what field mapping needs.
SCHEMA_DEPTH = 2


def ref_name(node):
    if not isinstance(node, dict):
        return None
    if "$ref" in node:
        return node["$ref"].rsplit("/", 1)[-1]
    if "allOf" in node and node["allOf"] and "$ref" in node["allOf"][0]:
        return node["allOf"][0]["$ref"].rsplit("/", 1)[-1]
    if node.get("type") == "array":
        inner = ref_name(node.get("items", {}))
        return f"{inner}[]" if inner else "array"
    return None


def first_sentence(text):
    return " ".join((text or "").split()).split(". ")[0][:DESCRIPTION_CHARS]


def print_schema(components, name, depth=0, seen=None):
    seen = seen or set()
    schema = components.get(name)
    if not schema:
        print(f"{'  ' * depth}(no component named {name})")
        return
    for field, node in (schema.get("properties") or {}).items():
        kind = ref_name(node) or node.get("type", "?")
        desc = first_sentence(node.get("description"))
        print(f"{'  ' * depth}{field}: {kind}" + (f"  -- {desc}" if desc else ""))
        inner = (ref_name(node) or "").rstrip("[]")
        if inner and inner in components and depth < SCHEMA_DEPTH and inner not in seen:
            seen.add(inner)
            print_schema(components, inner, depth + 1, seen)


def print_events(components):
    print("== WEBHOOK PAYLOAD FAMILIES (schema | slugs | x-origin-webhook-resource)")
    for name, schema in components.items():
        slugs = schema.get("x-origin-webhook-events")
        if not slugs:
            continue
        print(f"{name} | {slugs} | resource={schema.get('x-origin-webhook-resource')}")
        print_schema(components, name, depth=1)


def load_spec(path):
    try:
        with open(path, encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)
    except FileNotFoundError:
        sys.stderr.write(f"{path}: not found. Fetch it first (command in --help).\n")
        return None
    except yaml.YAMLError as err:
        sys.stderr.write(f"{path}: not valid YAML ({err}).\n")
        return None
    if not isinstance(spec, dict) or "components" not in spec or "info" not in spec:
        sys.stderr.write(f"{path}: not an OpenAPI document (no `info` or `components`).\n")
        return None
    components = (spec.get("components") or {}).get("schemas") or {}
    if not any("x-origin-webhook-events" in s for s in components.values() if isinstance(s, dict)):
        sys.stderr.write(
            f"{path}: no schema carries `x-origin-webhook-events`; is this the Origin spec?\n"
        )
        return None
    return spec


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1
    spec = load_spec(argv[1])
    if spec is None:
        return 1
    components = spec["components"]["schemas"]
    schema_mode = len(argv) > 2 and argv[2] == "schema"
    if schema_mode and len(argv) < 4:
        sys.stderr.write("schema mode needs a component name.\n")
        return 1
    print(f"# {spec['info'].get('title')} {spec['info'].get('version')}")
    if schema_mode:
        print_schema(components, argv[3])
    else:
        print_events(components)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
