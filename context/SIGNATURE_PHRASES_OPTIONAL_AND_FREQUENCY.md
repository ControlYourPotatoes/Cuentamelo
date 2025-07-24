, he# Signature Phrases: Optionality & Frequency

## Rationale

- Not all personalities use signature phrases.
- Frequency attribute allows for realistic, context-aware use.

## Config Example

"signature_phrases": [
{"text": "¡Vamos Vaqueros!", "frequency": "common"},
{"text": "Pa'lante siempre, broki.", "frequency": "rare"}
]

## Agent Logic

- Use signature phrases according to their frequency.
- For most personalities, signature phrases should be rare or omitted.
- For influencers/entertainers, use more frequently.

## Validation

- Only require signature phrases for personalities that need them.
- Each phrase must have a `text`; `frequency` is optional.

## Implementation Steps

1. Update data model and config.
2. Update loader and validation.
3. Update agent logic.
4. Update tests.
5. Document the change.
