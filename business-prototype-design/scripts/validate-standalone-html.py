#!/usr/bin/env python3

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


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
        parsed = urlparse(value.strip())
        return parsed.scheme in {"data", "blob"} or value.startswith(("#", "javascript:"))

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "script":
            src = values.get("src")
            if src and not self._is_embedded(src):
                self.external_dependencies.append(("script", src))
            else:
                self._inside_script = True
                self._script_has_content = False
        elif tag == "style":
            self._inside_style = True
            self._style_has_content = False
        elif tag == "link" and values.get("rel", "").lower() == "stylesheet":
            href = values.get("href", "")
            if not self._is_embedded(href):
                self.external_dependencies.append(("stylesheet", href))
        elif tag in {"img", "source", "audio", "video", "iframe"}:
            for attribute in ("src", "srcset", "poster"):
                value = values.get(attribute)
                if value and not self._is_embedded(value):
                    self.external_dependencies.append((f"{tag}.{attribute}", value))

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
    parser.add_argument("--require", action="append", default=[], help="Text that must appear; repeatable.")
    args = parser.parse_args()

    if not args.html.is_file():
        print(f"ERROR: file not found: {args.html}", file=sys.stderr)
        return 2

    text = args.html.read_text(encoding="utf-8")
    document = DependencyParser()
    document.feed(text)

    css_external_urls = [
        match.group(1)
        for match in re.finditer(r"url\(\s*['\"]?((?:https?:)?//[^)'\"\s]+)", text, re.I)
    ]
    missing = [value for value in args.require if value not in text]
    errors = []

    if document.external_dependencies:
        errors.extend(f"external dependency {kind}: {value}" for kind, value in document.external_dependencies)
    if css_external_urls:
        errors.extend(f"external CSS URL: {value}" for value in css_external_urls)
    if document.inline_scripts == 0:
        errors.append("no nonempty inline script found")
    if document.inline_styles == 0:
        errors.append("no nonempty inline style found")
    if missing:
        errors.extend(f"missing required text: {value}" for value in missing)

    inline_svg_count = len(re.findall(r"<svg\b", text, re.I))
    print(f"file={args.html}")
    print(f"bytes={len(text.encode('utf-8'))}")
    print(f"inline_scripts={document.inline_scripts}")
    print(f"inline_styles={document.inline_styles}")
    print(f"inline_svg={inline_svg_count}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
