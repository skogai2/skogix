#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.0",
#   "pyyaml>=6.0",
# ]
# ///
"""Validate routing file(s) (type: router) against router.schema.json.

Usage: validate_router.py <file> [file...]
Exits 0 if all files passed, 1 if any failed. Prints one PASS/FAIL line per
file (+ details on FAIL).
"""

import json
import sys
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from referencing.jsonschema import Schema

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    import jsonschema
except ImportError:
    print(
        "ERROR: missing deps — run via: uv run validate_router.py "
        + "(or: pip install jsonschema pyyaml)"
    )
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts._lib import (  # noqa: E402
    FrontmatterParseError,
    JsonValue,
    RouterBodyParseError,
    extract_xml_sections,
    parse_frontmatter,
)

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "router.schema.json"


class ValidationIssue(Protocol):
    @property
    def path(self) -> Iterable[str | int]: ...

    @property
    def message(self) -> str: ...


class SchemaValidator(Protocol):
    def iter_errors(self, instance: JsonValue) -> Iterable[ValidationIssue]: ...


class ValidatorFactory(Protocol):
    def __call__(self, schema: Schema) -> SchemaValidator: ...


class SchemaLoader(Protocol):
    def __call__(self, source: str, /) -> Schema: ...


_validator_factory: ValidatorFactory = jsonschema.Draft202012Validator
_load_schema: SchemaLoader = json.loads


def validate_file(path: Path, schema: Schema) -> int:
    try:
        raw = path.read_text()
    except FileNotFoundError:
        print(f"FAIL  {path.name}")
        print("      file: missing")
        return 1

    try:
        fm = parse_frontmatter(raw)
    except FrontmatterParseError as error:
        print(f"FAIL  {path.name}")
        print(f"      frontmatter: {error}")
        return 1

    if fm is None:
        print(f"FAIL  {path.name}")
        print("      frontmatter: missing YAML frontmatter")
        return 1

    doc_type = fm.get("type")

    try:
        sections = extract_xml_sections(raw)
    except RouterBodyParseError as error:
        print(f"FAIL  {path.name}")
        print(f"      body: {error}")
        return 1
    doc: dict[str, JsonValue] = {
        "type": doc_type,
        "frontmatter": fm,
        "sections": sections,
    }

    validator = _validator_factory(schema)
    errors = sorted(
        validator.iter_errors(doc),
        key=lambda error: tuple(str(piece) for piece in error.path),
    )

    if errors:
        print(f"FAIL  {path.name}")
        for err in errors:
            err_path = " > ".join(str(p) for p in err.path) or "(root)"
            print(f"      {err_path}: {err.message}")
        return 1

    print(f"PASS  {path.name}")
    return 0


def main() -> None:
    if not sys.argv[1:]:
        print("Usage: validate_router.py <file> [file...]", file=sys.stderr)
        sys.exit(1)

    schema = _load_schema(SCHEMA_PATH.read_text())
    fail = 0
    for arg in sys.argv[1:]:
        if validate_file(Path(arg).resolve(), schema):
            fail = 1
    sys.exit(fail)


if __name__ == "__main__":
    main()
