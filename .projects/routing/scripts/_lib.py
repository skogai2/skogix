"""Share typed frontmatter and XML parsing across the routing command-line tools."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, TypeAlias, TypeGuard

import yaml

_FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\n(?P<body>.*?)\n---[ \t]*(?:\n|\Z)",
    re.DOTALL,
)
_ROUTES_TAG_COUNT = 2
_FRONTMATTER_MAPPING_ERROR = "frontmatter must be a YAML mapping"
_FRONTMATTER_ORDER_ERROR = "frontmatter must precede the routes block"
_ROUTES_COUNT_ERROR = "body must contain one <routes>...</routes> block and no other XML blocks"
_ROUTES_PAIR_ERROR = (
    "routes tags must be an attribute-free opening and closing pair on separate lines"
)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
Frontmatter: TypeAlias = dict[str, JsonValue]


class UnknownValue(Protocol):
    pass


class SafeYamlLoad(Protocol):
    def __call__(self, source: str, /) -> UnknownValue: ...


_safe_yaml_load: SafeYamlLoad = yaml.safe_load


class FrontmatterParseError(ValueError):
    pass


class RouterBodyParseError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class XmlTagLine:
    line_number: int
    name: str
    closing: bool
    has_attributes: bool


def _is_unknown_list(value: UnknownValue) -> TypeGuard[list[UnknownValue]]:
    return isinstance(value, list)


def _is_unknown_mapping(
    value: UnknownValue,
) -> TypeGuard[dict[UnknownValue, UnknownValue]]:
    return isinstance(value, dict)


def _is_json_value(value: UnknownValue) -> TypeGuard[JsonValue]:
    if value is None or isinstance(value, str | int | float | bool):
        return True
    if _is_unknown_list(value):
        return all(_is_json_value(item) for item in value)
    if _is_unknown_mapping(value):
        return all(isinstance(key, str) and _is_json_value(entry) for key, entry in value.items())
    return False


def _is_frontmatter(value: UnknownValue) -> TypeGuard[Frontmatter]:
    return _is_unknown_mapping(value) and all(
        isinstance(key, str) and _is_json_value(entry) for key, entry in value.items()
    )


def _extract_standalone_xml_tags(lines: list[str]) -> list[XmlTagLine]:
    tags: list[XmlTagLine] = []
    fence_marker: str | None = None
    for line_number, line in enumerate(lines):
        stripped = line.strip()
        if fence_marker is not None:
            if stripped.startswith(fence_marker):
                fence_marker = None
            continue
        if stripped.startswith(("```", "~~~")):
            fence_marker = stripped[:3]
            continue

        tag_pattern = (
            r"<(?P<closing>/)?(?P<name>[A-Za-z][A-Za-z0-9_-]*)" + r"(?P<attributes>\s[^>]*)?>"
        )
        match = re.fullmatch(tag_pattern, stripped)
        if match is not None:
            tags.append(
                XmlTagLine(
                    line_number=line_number,
                    name=match.group("name"),
                    closing=match.group("closing") is not None,
                    has_attributes=match.group("attributes") is not None,
                )
            )
    return tags


def parse_frontmatter(text: str) -> Frontmatter | None:
    m = _FRONTMATTER_PATTERN.match(text)
    if not m:
        return None
    try:
        loaded = _safe_yaml_load(m.group("body"))
    except yaml.YAMLError as error:
        raise FrontmatterParseError(str(error)) from error
    if not _is_frontmatter(loaded):
        raise FrontmatterParseError(_FRONTMATTER_MAPPING_ERROR)
    return loaded


def is_router(fm: Mapping[str, JsonValue] | None) -> bool:
    return bool(fm) and fm.get("type") == "router"


def extract_xml_tags(text: str) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"</?([A-Za-z][A-Za-z0-9_-]*)[^>]*>", text):
        name = m.group(1)
        if name not in seen:
            tags.append(name)
            seen.add(name)
    return tags


def extract_xml_sections(text: str) -> list[JsonValue]:
    frontmatter = _FRONTMATTER_PATTERN.match(text)
    if frontmatter is None:
        raise RouterBodyParseError(_FRONTMATTER_ORDER_ERROR)

    body_lines = text[frontmatter.end() :].splitlines()
    tags = _extract_standalone_xml_tags(body_lines)
    if len(tags) != _ROUTES_TAG_COUNT:
        raise RouterBodyParseError(_ROUTES_COUNT_ERROR)
    opening, closing = tags
    valid_pair = (
        opening.name == "routes"
        and not opening.closing
        and not opening.has_attributes
        and closing.name == "routes"
        and closing.closing
        and not closing.has_attributes
        and opening.line_number < closing.line_number
    )
    if not valid_pair:
        raise RouterBodyParseError(_ROUTES_PAIR_ERROR)

    content = "\n".join(body_lines[opening.line_number + 1 : closing.line_number]).strip()
    return [{"kind": "xml", "name": "routes", "content": content}]
