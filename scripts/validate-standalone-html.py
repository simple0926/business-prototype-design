#!/usr/bin/env python3

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


CONTRACT_SECTIONS = ["REQUIREMENTS", "ROLES", "FLOWS", "PAGE_GUIDES", "VERSION"]


class DependencyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external_dependencies = []
        self.inline_scripts = 0
        self.inline_styles = 0
        self._inside_script = False
        self._inside_style = False
        self._script_has_content = False
        self._style_has_content = False
        self.script_text = []
        self.style_text = []

    @staticmethod
    def _is_embedded(value):
        if not value:
            return True
        value = value.strip()
        parsed = urlparse(value)
        return parsed.scheme == "data" or value.startswith(("#", "javascript:"))

    def _record(self, kind, value):
        if value and not self._is_embedded(value):
            self.external_dependencies.append((kind, value))

    def _record_srcset(self, tag, value):
        if not value:
            return
        value = value.strip()
        if value.lower().startswith("data:"):
            if value.count(",") != 1:
                self.external_dependencies.append(
                    (f"{tag}.srcset", "ambiguous or multiple data candidates")
                )
            return
        for candidate in value.split(","):
            reference = candidate.strip().split()[0] if candidate.strip() else ""
            self._record(f"{tag}.srcset", reference)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "script":
            src = values.get("src")
            if src:
                self._record("script", src)
            else:
                self._inside_script = True
                self._script_has_content = False
        elif tag == "style":
            self._inside_style = True
            self._style_has_content = False
        elif tag == "link":
            rel = set(values.get("rel", "").lower().split())
            if rel & {"stylesheet", "icon", "manifest", "preload", "modulepreload"}:
                self._record(f"link.{','.join(sorted(rel))}", values.get("href", ""))
        elif tag in {"img", "source", "audio", "video", "iframe", "embed", "image", "use"}:
            for attribute in ("src", "poster"):
                self._record(f"{tag}.{attribute}", values.get(attribute))
            self._record_srcset(tag, values.get("srcset"))
            if tag in {"image", "use"}:
                self._record(f"{tag}.href", values.get("href") or values.get("xlink:href"))
        elif tag == "object":
            self._record("object.data", values.get("data"))

    def handle_endtag(self, tag):
        if tag == "script" and self._inside_script:
            if self._script_has_content:
                self.inline_scripts += 1
            self._inside_script = False
        elif tag == "style" and self._inside_style:
            if self._style_has_content:
                self.inline_styles += 1
            self._inside_style = False

    def handle_data(self, data):
        if self._inside_script and data.strip():
            self._script_has_content = True
            self.script_text.append(data)
        if self._inside_style and data.strip():
            self._style_has_content = True
            self.style_text.append(data)


def validate_contract_sections(text, errors):
    for section in CONTRACT_SECTIONS:
        pattern = re.compile(
            rf"<!--\s*BPD:{section}:START\s*-->(.*?)<!--\s*BPD:{section}:END\s*-->",
            re.I | re.S,
        )
        match = pattern.search(text)
        if not match:
            errors.append(f"missing BPD contract section: {section}")
            continue
        visible = re.sub(r"<[^>]+>", " ", match.group(1))
        visible = re.sub(r"\s+", " ", visible).strip()
        if len(visible) < 20:
            errors.append(f"BPD contract section is not substantive: {section}")


def code_mask(text, css=False):
    output = list(text)
    mode = "code"
    template_depth = None
    index = 0
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if mode == "code":
            if not css and char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                mode = "line_comment"
                index += 2
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                mode = "block_comment"
                index += 2
                continue
            if char in {"'", '"'}:
                output[index] = " "
                mode = "single" if char == "'" else "double"
                index += 1
                continue
            if not css and char == "`":
                output[index] = " "
                mode = "template"
                index += 1
                continue
            if template_depth is not None:
                if char == "{":
                    template_depth += 1
                elif char == "}":
                    template_depth -= 1
                    if template_depth == 0:
                        output[index] = " "
                        template_depth = None
                        mode = "template"
            index += 1
            continue

        output[index] = "\n" if char == "\n" else " "
        if mode == "line_comment" and char == "\n":
            mode = "code"
        elif mode == "block_comment" and char == "*" and following == "/":
            output[index + 1] = " "
            mode = "code"
            index += 2
            continue
        elif mode in {"single", "double", "template"} and char == "\\":
            if index + 1 < len(text):
                output[index + 1] = "\n" if text[index + 1] == "\n" else " "
            index += 2
            continue
        elif mode == "single" and char == "'":
            mode = "code"
        elif mode == "double" and char == '"':
            mode = "code"
        elif mode == "template" and char == "`":
            mode = "code"
        elif mode == "template" and char == "$" and following == "{":
            output[index + 1] = " "
            template_depth = 1
            mode = "code"
            index += 2
            continue
        index += 1
    return "".join(output)


def decode_css_identifiers(text):
    text = re.sub(
        r"\\([0-9a-fA-F]{1,6})\s?",
        lambda match: chr(int(match.group(1), 16)),
        text,
    )
    return re.sub(r"\\([^0-9a-fA-F\n])", r"\1", text)


def main():
    parser = argparse.ArgumentParser(description="Validate an offline standalone HTML prototype.")
    parser.add_argument("html", type=Path)
    parser.add_argument("--require", action="append", default=[], help="Additional text that must appear; repeatable.")
    parser.add_argument(
        "--skip-contract-markers",
        action="store_true",
        help="Skip default BPD document markers for a deliberately narrowed deliverable.",
    )
    args = parser.parse_args()

    if not args.html.is_file():
        print(f"ERROR: file not found: {args.html}", file=sys.stderr)
        return 2

    text = args.html.read_text(encoding="utf-8")
    document = DependencyParser()
    document.feed(text)
    errors = []

    if args.skip_contract_markers and not args.require:
        errors.append("--skip-contract-markers requires at least one explicit --require value")

    for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", text, re.I | re.S):
        value = match.group(2).strip()
        if value and not document._is_embedded(value):
            errors.append(f"external CSS URL: {value}")

    style_text = decode_css_identifiers(code_mask("\n".join(document.style_text), css=True))
    if re.search(r"@import\b", style_text, re.I):
        errors.append("external CSS @import is not allowed")

    script_text = code_mask("\n".join(document.script_text))
    if re.search(r"(?<![\w$.])import\b(?!\s*\.\s*meta\b)", script_text):
        errors.append("external JavaScript import is not allowed")
    if re.search(r"(?:^|[;\n])\s*export\b[^;\n]*\bfrom\b", script_text, re.I):
        errors.append("external JavaScript export-from is not allowed")
    for label, pattern in {
        "fetch": r"(?<![\w$.])fetch\s*\(",
        "worker": r"(?<![\w$.])(?:Worker|SharedWorker)\s*\(",
        "service worker": r"serviceWorker\s*\.\s*register\s*\(",
    }.items():
        if re.search(pattern, script_text):
            errors.append(f"external JavaScript {label} is not allowed")

    errors.extend(f"external dependency {kind}: {value}" for kind, value in document.external_dependencies)
    if document.inline_scripts == 0:
        errors.append("no nonempty inline script found")
    if document.inline_styles == 0:
        errors.append("no nonempty inline style found")

    required = list(args.require)
    for value in required:
        if value not in text:
            errors.append(f"missing required text: {value}")
    if not args.skip_contract_markers:
        validate_contract_sections(text, errors)

    inline_svg_count = len(re.findall(r"<svg\b", text, re.I))
    print(f"file={args.html}")
    print(f"bytes={len(text.encode('utf-8'))}")
    print(f"inline_scripts={document.inline_scripts}")
    print(f"inline_styles={document.inline_styles}")
    print(f"inline_svg={inline_svg_count}")
    print(f"contract_markers={'skipped' if args.skip_contract_markers else 'checked'}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
