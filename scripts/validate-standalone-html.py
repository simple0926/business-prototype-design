#!/usr/bin/env python3

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


CONTRACT_MARKERS = [
    "BPD:REQUIREMENTS",
    "BPD:ROLES",
    "BPD:FLOWS",
    "BPD:PAGE_GUIDES",
    "BPD:VERSION",
]


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
        elif tag in {"img", "source", "audio", "video", "iframe", "embed"}:
            for attribute in ("src", "srcset", "poster"):
                self._record(f"{tag}.{attribute}", values.get(attribute))
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
        if self._inside_style and data.strip():
            self._style_has_content = True


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

    for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", text, re.I | re.S):
        value = match.group(2).strip()
        if value and not document._is_embedded(value):
            errors.append(f"external CSS URL: {value}")

    javascript_patterns = {
        "dynamic import": r"\bimport\(\s*['\"]([^'\"]+)['\"]\s*\)",
        "fetch": r"\bfetch\(\s*['\"]([^'\"]+)['\"]",
        "worker": r"\b(?:Worker|SharedWorker)\(\s*['\"]([^'\"]+)['\"]",
        "service worker": r"serviceWorker\.register\(\s*['\"]([^'\"]+)['\"]",
    }
    for kind, pattern in javascript_patterns.items():
        for value in re.findall(pattern, text, re.I):
            if not document._is_embedded(value):
                errors.append(f"external JavaScript {kind}: {value}")

    errors.extend(f"external dependency {kind}: {value}" for kind, value in document.external_dependencies)
    if document.inline_scripts == 0:
        errors.append("no nonempty inline script found")
    if document.inline_styles == 0:
        errors.append("no nonempty inline style found")

    required = list(args.require)
    if not args.skip_contract_markers:
        required.extend(CONTRACT_MARKERS)
    for value in required:
        if value not in text:
            errors.append(f"missing required text: {value}")

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
