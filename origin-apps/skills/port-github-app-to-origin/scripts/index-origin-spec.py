#!/usr/bin/env python3
"""Print a grep-friendly index of the Origin OpenAPI spec.

Usage:
    python3 index-origin-spec.py openapi.yaml            # everything
    python3 index-origin-spec.py openapi.yaml ops        # operations only
    python3 index-origin-spec.py openapi.yaml events     # webhook payload families
    python3 index-origin-spec.py openapi.yaml scopes     # scope catalog
    python3 index-origin-spec.py openapi.yaml schema PullRequest   # one component

Fetch the spec first:
    curl -sSL https://cursor.com/docs/api/origin/openapi.yaml -o openapi.yaml

Read-only. Needs PyYAML (`pip install pyyaml`). Everything printed comes from
the spec you pass in; nothing is pinned or embedded here.
"""

import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "PyYAML is not installed. Run `pip install pyyaml`, or read the spec "
        "directly (search for `operationId:`, `x-origin-scopes:`, and "
        "`x-origin-webhook-events:`).\n"
    )
    sys.exit(2)

METHODS = ("get", "post", "put", "patch", "delete")


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
    return " ".join((text or "").split()).split(". ")[0][:140]


def print_schema(components, name, depth=0, seen=None, max_depth=2):
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
        if inner and inner in components and depth < max_depth and inner not in seen:
            seen.add(inner)
            print_schema(components, inner, depth + 1, seen, max_depth)


def print_ops(spec):
    print("== OPERATIONS (operationId | METHOD path | scopes | tokenTypes | ambient | visibility)")
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            if method not in METHODS:
                continue
            xs = op.get("x-origin-scopes") or {}
            params = [p["name"] for p in op.get("parameters", [])]
            body = None
            rb = op.get("requestBody")
            if rb:
                schema = rb["content"]["application/json"]["schema"]
                body = ref_name(schema) or list((schema.get("properties") or {}).keys())
            resp = (
                op.get("responses", {})
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            print(
                f"{op.get('operationId')} | {method.upper()} {path} | "
                f"scopes={xs.get('scopes')} tokenTypes={xs.get('tokenTypes')} "
                f"ambient={xs.get('ambient')} visibility={op.get('x-cursor-visibility')}"
            )
            print(f"    params={params} body={body} -> {ref_name(resp) or '(empty)'}")
            print(f"    {first_sentence(op.get('description'))}")


def print_events(spec):
    components = spec["components"]["schemas"]
    print("== WEBHOOK PAYLOAD FAMILIES (schema | slugs | x-origin-webhook-resource)")
    for name, schema in components.items():
        slugs = schema.get("x-origin-webhook-events")
        if not slugs:
            continue
        print(f"{name} | {slugs} | resource={schema.get('x-origin-webhook-resource')}")
        print_schema(components, name, depth=1, max_depth=2)


def print_scopes(spec):
    print("== SCOPES (scope | tokenTypes seen | operations)")
    table = {}
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            if method not in METHODS:
                continue
            xs = op.get("x-origin-scopes") or {}
            for scope in xs.get("scopes") or []:
                entry = table.setdefault(scope, {"tokens": set(), "ops": [], "ambient": False})
                entry["tokens"].update(xs.get("tokenTypes") or [])
                entry["ops"].append(op.get("operationId"))
                entry["ambient"] = entry["ambient"] or bool(xs.get("ambient"))
    for scope in sorted(table):
        e = table[scope]
        print(f"{scope} | tokenTypes={sorted(e['tokens'])} ambient={e['ambient']} | {e['ops']}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    with open(argv[1], encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    mode = argv[2] if len(argv) > 2 else "all"
    print(f"# {spec['info'].get('title')} {spec['info'].get('version')}")
    if mode == "schema":
        print_schema(spec["components"]["schemas"], argv[3])
        return 0
    if mode in ("ops", "all"):
        print_ops(spec)
    if mode in ("events", "all"):
        print_events(spec)
    if mode in ("scopes", "all"):
        print_scopes(spec)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
