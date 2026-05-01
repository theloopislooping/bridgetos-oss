# bridgetos-schema

The data contract for BridgetOS observations. This is the schema agents emit when sending output to the BridgetOS API for behavioral identity monitoring.

## Files

- `observation-v1.json` — JSON Schema (Draft 2020-12) defining a single observation
- `examples/` — example observations for common scenarios

## Versioning

The schema is versioned via the `$id` URL and the `schema_version` field on each observation. Breaking changes will increment the major version (`v1` → `v2`); additive changes will be backward-compatible within a major version.

## Using the schema

### Validation in Python (jsonschema)

```python
import json
from jsonschema import validate

with open("observation-v1.json") as f:
    schema = json.load(f)

observation = {
    "agent_id": "support-bot-001",
    "timestamp": "2026-05-01T18:00:00Z",
    "schema_version": "1.0",
    "content": {"text": "I can help you with that refund request."},
    "context": {"task_type": "customer_support", "model": "claude-opus-4-7"}
}

validate(observation, schema)
```

### Validation in TypeScript (ajv)

```typescript
import Ajv from "ajv";
import schema from "./observation-v1.json";

const ajv = new Ajv();
const validate = ajv.compile(schema);

const observation = {
  agent_id: "support-bot-001",
  timestamp: "2026-05-01T18:00:00Z",
  schema_version: "1.0",
  content: { text: "I can help you with that refund request." }
};

if (!validate(observation)) {
  console.error(validate.errors);
}
```

## License

MIT
