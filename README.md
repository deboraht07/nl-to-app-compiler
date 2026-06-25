# NL-to-App Compiler

**Live Demo:** https://nl-to-app-compilr.onrender.com

A multi-stage pipeline that converts natural language app descriptions into validated, cross-consistent application schemas (UI, API, Database, and Auth) and proves the output is directly usable by rendering a real working preview from it, with no manual fixes.

This is built as a compiler, not a prompt: natural language is parsed into a structured intermediate form, progressively refined through typed stages, validated against a strict schema contract, and automatically repaired when the model's output doesn't hold up.

## Architecture

```text
User prompt (NL)
   │
   ▼

[Stage 1] Intent Extraction
    → structured JSON: entities, roles, features, assumptions
   │
   ▼

[Stage 2] System Design
    → intent → entities+fields, roles+permissions, pages
   │
   ▼

[Stage 3] Schema Generation
    → design → ui_schema, api_schema, db_schema, auth_schema
   │
   ▼

[Stage 4] Cross-Layer Validator
    → pure code, no LLM. Checks consistency across all 4 schemas
   │
   ├── valid → done
   └── invalid → [Repair Layer]
                 → targeted regeneration of only the broken layer(s)
                 → re-validate
   │
   ▼

[Runtime]
    → renders a real, working HTML preview from the validated schema + sample data
```

Every stage is a separate, independently testable module (`/stages`, `/validator`, `/runtime`).

A single combined prompt was deliberately rejected: splitting generation lets the validator pinpoint exactly which layer broke, and lets repair fix only that layer instead of regenerating everything from scratch.

## Why Multi-Stage, Not a Single Prompt

A single prompt asked to produce UI, API, DB, and Auth schemas simultaneously gives you no way to check or partially correct the result — if anything is wrong, the only option is to regenerate everything and hope.

Splitting generation into stages, each with a real schema contract (Pydantic) at its boundary, means failures are localized, diagnosable, and individually repairable. This is the difference between a script that calls an LLM and a system that controls one.

## Validation + Repair Engine

This is the core of the system.

`validator/cross_layer.py` checks what a type system alone cannot:

* Every entity and field referenced in the UI schema actually exists in the DB schema
* Every entity referenced in the API schema exists in the DB schema
* Every role referenced anywhere exists in the Auth schema
* Every page has at least one renderable component — an empty page is treated as a generation failure, not a quirk

When validation fails, `validator/repair.py` groups errors by the layer they belong to and sends a **targeted repair prompt** — containing only the specific errors and the broken layer's current JSON — back to the model, instead of regenerating the whole schema.

Up to three repair attempts are made before the system surfaces a clear, typed failure rather than crashing.

This was validated two ways:

1. **Fault injection.** Valid output was deliberately corrupted — an unknown entity reference, an unknown role, a hallucinated field — to confirm the validator catches exactly the injected faults, with the correct layer and message, and that repair resolves them in a single pass.

2. **Natural failure testing.** The identical real-world prompt was run repeatedly against the model. Across four consecutive runs, two returned clean and two produced naturally occurring incomplete UI schemas (missing components). Both natural failures were detected and fully repaired by the second attempt.

This is the stronger evidence: the system recovers from real model unreliability, not just staged test cases.

## Execution Awareness

`runtime/renderer.py` takes the final, validated schema and a generated mock dataset and produces a real, styled HTML application: data tables, working-looking forms, and trend charts — all driven entirely by the schema, with no per-app hardcoding.

This is the proof that the generated JSON is directly executable, not just structurally valid.

The current renderer proves the UI layer is real and usable. Form submissions surface a clear static-preview notice rather than writing to a live store — this is a deliberate scope boundary, not an oversight.

The natural next extension is a generated mock API server (an in-memory store matching the DB schema) wired to the same rendered forms and tables for a full round-trip execution proof.

## Evaluation Framework

`eval/eval_runner.py` runs a curated set of real product prompts and edge cases — vague, conflicting, underspecified, and intentionally oversized scope — logging success rate, repair attempts, latency, and failure type for every run.

Results are written to:

```text
eval/eval_results.csv
```

**Latest run: 90% success rate, 35.8s average latency, 3 repair attempts triggered across the set.**

The one failure in the current set is a deliberately oversized prompt requesting nine or more distinct entities/features in a single app.

It fails cleanly with a typed error (`missing keys after repair attempt`) rather than crashing — a known and explicitly identified scale limit of single-pass generation, not a silent defect.

The natural fix, and the next item on the roadmap, is scope detection that decomposes oversized requests into multiple sub-generation passes instead of one large call.

## Cost vs Quality Tradeoff

Two model tiers were evaluated directly, not assumed:

* A larger, more capable model produced more consistently complete schemas but came with a far tighter request budget, which is a real constraint at any meaningful usage volume.
* A smaller, faster model offers a substantially larger usable budget and lower latency, at the cost of measurably less consistency — the same prompt produced fully populated schemas roughly half the time, with the rest needing repair.

The system is built around the smaller, cheaper model **by design**, using the validation and repair layer to recover the reliability gap that introduces.

This is a deliberate architectural choice: pay for quality with cheap, targeted repair calls only when generation actually falls short, rather than paying premium-model cost on every single request regardless of whether it was needed.

The eval data backs this directly — repair attempts cluster exactly on the runs where the cheaper model under-delivered, and zero repairs were needed otherwise.

The natural production extension is a quality-tiered router: default to the fast/cheap model, and escalate to a larger model automatically only for requests that fail repair more than once — spending more only where cheap generation has already proven insufficient.

## Roadmap / Next Steps

* Explicit clarification-prompting for severely underspecified input, as an alternative to the current assumption-logging strategy (both are valid handling strategies; assumption-logging was implemented first)
* A generated mock API server wired to the rendered UI for full round-trip execution
* Scope decomposition for oversized, multi-domain requests
* Expanded evaluation set with a wider range of real-world product prompts
* Detection of duplicate routes, table names, and field names within a single schema
* Fuzzy-mapping unknown entity references to the closest existing entity instead of failing outright
* A dedicated `detail` / `view` component type, distinct from `form`, for read-only pages (e.g. "View Student Details" currently renders as an editable form)
* Auto-generation of a login/auth endpoint to match any generated Login page

## Running Locally

```bash
pip install -r requirements.txt

# create a .env file with GROQ_API_KEY=your_key
# see .env.example

uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Running the Evaluation

```bash
python eval/eval_runner.py
```

Results are written to:

```text
eval/eval_results.csv
```
