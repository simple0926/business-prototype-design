#!/usr/bin/env python3

import json
from pathlib import Path


CLASSIFICATIONS = {"business", "visual", "mixed", "out_of_scope"}
VISUAL_METHODS = {"render", "visual"}


def resolve_path(base, value):
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_manifest(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"invalid evidence manifest: {error}"]


def validate_manifest(path):
    path = Path(path).resolve()
    manifest, errors = load_manifest(path)
    if manifest is None:
        return errors, {"sources": 0, "units": 0}

    if manifest.get("schema_version") != "0.3":
        errors.append(f"unsupported evidence manifest schema_version: {manifest.get('schema_version')!r}")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("evidence manifest requires a nonempty sources list")
        return errors, {"sources": 0, "units": 0}

    source_ids = set()
    unit_count = 0
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source entry must be an object")
            continue
        source_id = source.get("source_id")
        if not source_id:
            errors.append("source entry requires source_id")
            source_id = "<missing>"
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)

        source_path = source.get("path")
        if not source_path:
            errors.append(f"{source_id}: source path is required")
        elif not resolve_path(path.parent, source_path).is_file():
            errors.append(f"{source_id}: source path not found: {source_path}")
        if not source.get("authority"):
            errors.append(f"{source_id}: authority is required")
        if source.get("kind") not in {"pdf", "image", "document", "code", "other"}:
            errors.append(f"{source_id}: unsupported kind {source.get('kind')!r}")

        total_units = source.get("total_units")
        if not isinstance(total_units, int) or total_units < 1:
            errors.append(f"{source_id}: total_units must be a positive integer")
            continue
        units = source.get("units")
        if not isinstance(units, list):
            errors.append(f"{source_id}: units must be a list")
            continue
        unit_count += len(units)
        sequences = []
        for unit in units:
            if not isinstance(unit, dict):
                errors.append(f"{source_id}: unit entry must be an object")
                continue
            sequence = unit.get("sequence")
            if not isinstance(sequence, int):
                errors.append(f"{source_id}: unit sequence must be an integer")
                continue
            sequences.append(sequence)
            unit_label = unit.get("unit_id") or f"unit-{sequence}"
            if unit.get("inspected") is not True:
                errors.append(f"{source_id}/{unit_label}: unit is not inspected")
            methods = set(unit.get("inspection_methods") or [])
            if not methods:
                errors.append(f"{source_id}/{unit_label}: inspection_methods are required")
            if source.get("requires_visual_review") is True and not methods.intersection(VISUAL_METHODS):
                errors.append(f"{source_id}/{unit_label}: visual review requires render or visual inspection")
            classification = unit.get("classification")
            if classification not in CLASSIFICATIONS:
                errors.append(f"{source_id}/{unit_label}: unsupported classification {classification!r}")
            if classification == "out_of_scope":
                if not unit.get("notes"):
                    errors.append(f"{source_id}/{unit_label}: out_of_scope unit requires notes")
            elif not unit.get("evidence_ids"):
                errors.append(f"{source_id}/{unit_label}: in-scope unit requires evidence_ids")

        expected = set(range(1, total_units + 1))
        actual = set(sequences)
        missing = sorted(expected - actual)
        duplicates = sorted(number for number in actual if sequences.count(number) > 1)
        out_of_range = sorted(actual - expected)
        if missing:
            errors.append(f"{source_id}: missing unit coverage: {', '.join(map(str, missing))}")
        if duplicates:
            errors.append(f"{source_id}: duplicate unit coverage: {', '.join(map(str, duplicates))}")
        if out_of_range:
            errors.append(f"{source_id}: out-of-range units: {', '.join(map(str, out_of_range))}")

    return errors, {"sources": len(sources), "units": unit_count}
