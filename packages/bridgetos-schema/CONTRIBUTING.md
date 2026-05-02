# Contributing to bridgetos-schema

This package is the observation data contract. It is a single JSON Schema file (`observation-v1.json`) with example payloads in `examples/`.

## Validation

```bash
uv run --with check-jsonschema check-jsonschema --check-metaschema observation-v1.json
```

This validates the schema file itself against the JSON Schema meta-schema (catches bad `$ref`, unknown keywords, malformed JSON). CI runs this on every push.

## Adding example payloads

Add new files to `examples/`. Each example must be a valid observation that passes schema validation:

```bash
uv run --with check-jsonschema check-jsonschema --schemafile observation-v1.json examples/my-example.json
```

Examples should illustrate a realistic use case — not just the minimum required fields.

## Schema versioning rules

`observation-v1.json` is the current version. The version number is part of the filename and the `$id`.

**Non-breaking (no version bump required):**
- Adding a new optional field (no `required` entry, has a default or is nullable)
- Expanding an enum to allow additional values
- Loosening a constraint (e.g., increasing `maxLength`)

**Breaking (requires a new version file `observation-v2.json`):**
- Removing or renaming any existing field
- Changing a field's type
- Making an optional field required
- Tightening a constraint in a way that would reject previously valid payloads

When bumping to v2, keep `observation-v1.json` in place — existing integrations must not break. Add a `# Deprecated` note to v1 and document the migration path in `examples/`.

## What stays out of scope

The schema describes what agents emit. It does not encode scoring logic, governance thresholds, or anything about the analytic core — those live in the proprietary service.
