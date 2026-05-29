# bids2openminds: Multi-Stage Modernisation Meta-Plan

## Context

The current codebase uses pybids as its sole interface to BIDS datasets. The planned evolution has four stages, each building on the last:

1. Replace pybids with ancpBIDS (issues #69, #88)
2. Introduce bidsschematools into `mapping.py` for schema-driven term mapping
3. Enable BIDS validation via ancpBIDS
4. Use ancpBIDS's metadata inheritance engine to generate in-depth openMINDS metadata (neuroimaging, specimenPrep, etc.)

Stages 1–3 are housekeeping; stage 4 is the major feature that motivates the earlier work.

---

## Stage 1 — Replace pybids with ancpBIDS

### What changes

`converter.py` currently does:
```python
from bids import BIDSLayout
bids_layout = BIDSLayout(input_path)
layout_df = bids_layout.to_df()            # → all files as DataFrame
subjects_id = bids_layout.get_subjects()
```

And `main.py` calls `layout.get_tasks()` and `layout.get_sessions()`.

`get_subjects/tasks/sessions` are drop-in replacements in ancpBIDS. The only real migration decision is what to do about `to_df()`.

---

### Key decision: keep the DataFrame or switch to native ancpBIDS objects?

**Option A — Keep the DataFrame (shim approach)**

Write a helper that converts `layout.get()` results into a DataFrame with the same columns pybids produced (`path`, `suffix`, `datatype`, `subject`, `session`, `extension`), then pass it through the rest of the pipeline unchanged.

| Pros | Cons |
|---|---|
| Zero changes to `main.py` or `utility.py` | Shim must replicate exact column names and NaN patterns — any discrepancy silently breaks downstream logic |
| Lower risk, easier to verify (existing tests pass) | Locks in pandas as the data model when ancpBIDS has a cleaner OO interface |
| Single-file change in `converter.py` | Carries forward a data model that becomes less relevant in Stage 4 |

**Option B — Switch to ancpBIDS native API**

Replace `layout_df` throughout with direct `layout.get(suffix=..., subject=...)` calls and refactor `utility.table_filter` / `pd_table_value` into thin wrappers around ancpBIDS queries.

| Pros | Cons |
|---|---|
| Idiomatic ancpBIDS usage; sets up Stage 4 naturally | Significant refactor of `main.py` and `utility.py` |
| No shim to maintain | Higher risk; larger diff; more test surface to verify |
| `create_file()` iterating ancpBIDS objects is cleaner than iterating DataFrame rows | |

**Recommendation**: Option A for Stage 1. The shim is a contained, verifiable change. Option B's refactor is better done alongside Stage 4 when the full metadata model is being reworked anyway — doing it twice (once now, once for the metadata extension) is wasteful.

### Shim implementation detail

ancpBIDS `layout.get(return_type='object')` returns a list of `Artifact` objects. Their attributes:
- `artifact.uri` — full file path (pybids called this `path`)
- `artifact.suffix`, `artifact.datatype`, `artifact.extension` — direct attributes, same names as pybids
- `artifact.entities` — list of `EntityRef` objects with `.key` and `.value` properties

**Critical difference:** ancpBIDS uses short BIDS entity keys (`sub`, `ses`, `task`) while pybids normalises `sub` → `subject` and `ses` → `session` in its DataFrame. The downstream code uses `file["subject"]` and `file["session"]` throughout. The shim must remap these:

```python
_ENTITY_RENAMES = {"sub": "subject", "ses": "session"}

def layout_to_df(layout):
    rows = []
    for artifact in layout.get(return_type='object'):
        row = {
            "path": artifact.uri,
            "suffix": artifact.suffix,
            "datatype": artifact.datatype,
            "extension": artifact.extension,
        }
        for entity in artifact.entities:
            key = _ENTITY_RENAMES.get(entity.key, entity.key)
            row[key] = entity.value
        rows.append(row)
    return pd.DataFrame(rows)
```

This goes in `converter.py` (or `utility.py`) and replaces the `bids_layout.to_df()` call. All downstream code in `main.py` and `utility.py` remains unchanged.

### Dependency changes

Both `"bids"` (pybids) and `"bids-validator == 1.14.6"` can be removed from `pyproject.toml`:
- `"bids"` is replaced by `"ancpbids"`
- `"bids-validator"` is a separate package that is imported in `converter.py` but only in a commented-out block — it is not used anywhere and can be dropped entirely

### Critical files
- `bids2openminds/converter.py` — replace import, `BIDSLayout()` call, `to_df()` call; add `layout_to_df()` shim; remove unused `BIDSValidator` import
- `pyproject.toml` — remove `"bids"` and `"bids-validator == 1.14.6"`; add `"ancpbids"`
- `test/test_task.py` — replace `BIDSLayout` import

### Verification
Run the full test suite (`pytest -v --cov=bids2openminds`), especially `test/test_bids_examples.py` which does end-to-end conversion on real BIDS datasets. Subject counts, file counts, and person counts should be identical to the pybids-based baseline.

---

## Stage 2 — Schema-driven mapping with bidsschematools

### What changes

`mapping.py` currently contains manually-maintained dicts whose BIDS keys (suffixes, datatypes) are hardcoded. New BIDS spec versions can add suffixes that silently go unmapped.

bidsschematools exposes `schema.objects.suffixes` and `schema.objects.datatypes` — the authoritative lists from the spec.

### Three approaches (pick one or combine)

**Approach A — Test-time completeness check**

Add a test that loads the schema and asserts that every suffix/datatype in the schema has an entry in `MAP_2_TECHNIQUES` / `MAP_2_EXPERIMENTAL_APPROACHES` (even if the value is `None`). Acts as a spec-update early-warning system. No runtime cost.

**Approach B — Schema-seeded mapping with explicit `None` for unknowns**

At module load time, use bidsschematools to build the complete key set, then overlay the hand-curated openMINDS values. Any suffix not yet mapped gets `None` explicitly (same as today's TODOs, but automatically kept complete). The openMINDS side of the mapping is still human-curated.

```python
import bidsschematools.schema as bst
_schema = bst.load_schema()
MAP_2_TECHNIQUES = {s: None for s in _schema.objects.suffixes} | _MANUAL_TECHNIQUES
```

**Approach C — BIDS-version-aware mapping**

Load the schema version matching the dataset's `BIDSVersion` field at conversion time, and filter/warn based on that. Most important once datasets using older BIDS versions become common.

**Recommendation**: A + B together for Stage 2. The test (A) is one file and zero risk; the schema-seeded mapping (B) eliminates the class of silent gaps. C can be deferred to Stage 4 when the metadata engine is version-aware anyway.

### Critical files
- `bids2openminds/mapping.py`
- `pyproject.toml` — add `"bidsschematools"` dependency
- New or extended test file to assert completeness

### Verification
Run the test suite. Separately, manually check that the schema-seeded `MAP_2_TECHNIQUES` keys are a superset of the current hardcoded keys (no regressions). Check that a conversion of a known dataset produces the same techniques/approaches as before.

---

## Stage 3 — BIDS validation

### What changes

`converter.py` has a commented-out TODO:
```python
# TODO use BIDSValidator to check if input directory is a valid BIDS directory
```

ancpBIDS provides `layout.validate()` which returns a structured `ValidationReport` with errors and warnings.

### Decision: how strict?

Many real-world BIDS datasets have minor spec violations (missing recommended fields, non-standard extensions). Hard-failing on any validation error would break the tool for a large fraction of real datasets.

**Options:**
- **Warn-only**: Print validation warnings but proceed; only raise on critical errors
- **Flag-controlled**: Add a `--strict` CLI flag; default is warn-only
- **Report integration**: Include validation summary in the existing report output (`report.py`)

**Recommendation**: Warn-only by default, with validation output folded into `report.py`. The `--strict` flag can raise on errors for CI/pipeline use. This matches how the existing `--quiet` flag controls output verbosity.

### Critical files
- `bids2openminds/converter.py` — call `layout.validate()` after `BIDSLayout()`
- `bids2openminds/report.py` — incorporate validation results into report
- CLI in `converter.py` — add optional `--strict` flag

### Verification
Test with a known-valid BIDS dataset (no warnings expected) and a deliberately invalid one (warnings expected, conversion still succeeds).

---

## Stage 4 — In-depth metadata via inheritance engine

### What this enables

The current output covers only coarse dataset-level metadata. The openMINDS `neuroimaging` and `specimenPrep` modules contain classes for acquisition parameters, MRI protocols, electrode configurations, tissue samples, etc. These require per-file or per-session metadata from JSON sidecars — the data that lives in BIDS sidecar files and follows the BIDS inheritance principle.

ancpBIDS's `layout.get_metadata(path)` resolves the full inherited metadata for any file, merging fields from dataset-level, datatype-level, and file-level sidecars in the correct order.

### What changes

This stage is the largest and most open-ended. The broad shape:

1. **Refactor the data model** (this is where Option B from Stage 1 becomes relevant): replace the DataFrame-centric pipeline in `main.py` with ancpBIDS-native object traversal, so that per-file metadata is naturally accessible alongside file paths.

2. **Extend `main.py`** with new functions (`create_mri_protocol`, `create_electrode_configuration`, `create_tissue_sample`, etc.) that read sidecar metadata and instantiate openMINDS neuroimaging/specimenPrep objects.

3. **Extend `mapping.py`** (or introduce a `mapping_neuroimaging.py`) to map BIDS acquisition parameters (RepetitionTime, EchoTime, MagneticFieldStrength, etc.) to openMINDS controlled terms.

4. **BIDS-version-aware schema** (Approach C from Stage 2): use the dataset's `BIDSVersion` to load the correct schema, since acquisition parameter names have changed between spec versions.

### Key dependency on earlier stages

- Requires Stage 1 (ancpBIDS must be the layout engine for `get_metadata()` to be available)
- Requires Stage 2 (schema-driven mapping provides the framework to extend to acquisition parameters)
- Stage 3 (validation) is independent but useful — invalid datasets produce unreliable metadata

### Mapping layer (done ahead of object creation)

The BIDS → openMINDS v5 *neuroimaging* (MRI) mapping data already lives in
`mapping.py` (the `MAP_2_MRI_*` / `MAP_2_CONTRAST_AGENT` / `MAP_2_ENCODING_DIRECTION`
value-translation dicts, plus the `BIDS_FIELD_2_OPENMINDS_PROPERTY` field→property
index), with validation in `test/test_neuroimaging_mapping.py`. The
object-creation code that consumes it is the remaining Stage 4 work.

**Future "FieldMap" direction.** `BIDS_FIELD_2_OPENMINDS_PROPERTY` is currently
plain `(class, property)` tuples. The intended evolution is to enrich each entry
into a structured descriptor `{class, property, kind}` (where `kind` is the value
shape — scalar / `QuantitativeValue` / array) and eventually fold the `MAP_2_*`
value-translation dicts into the same structure — a single source describing both
*where* each BIDS field goes and how to construct its value. (Kept as plain dicts
for now, for consistency with the existing `MAP_2_*` style.)

Units are always taken directly from the BIDS sidecar: openMINDS `QuantitativeValue`
carries its own unit, so values are copied across unchanged and never converted.

### Critical files (anticipated)
- `bids2openminds/main.py` — major extension
- `bids2openminds/converter.py` — wire up new functions
- `bids2openminds/mapping.py` — new controlled-term mappings for acquisition parameters
- New test files covering neuroimaging/specimenPrep object creation

### Verification
End-to-end conversion of a dataset with known acquisition parameters (e.g. an fMRI dataset with a `bold.json` sidecar containing RepetitionTime, EchoTime, etc.) and assert that the output openMINDS collection contains correctly populated MRI protocol objects.

---

## Dependency graph

```
Stage 1 (ancpBIDS)
    │
    ├── Stage 2 (bidsschematools in mapping.py)   [independent of Stage 1, but natural next step]
    │
    ├── Stage 3 (validation)                       [requires Stage 1]
    │
    └── Stage 4 (in-depth metadata)                [requires Stage 1; benefits from 2 and 3]
```

Stages 1 and 2 can be developed in parallel (different files, no conflicts). Stage 3 requires Stage 1. Stage 4 requires all of 1–2 and benefits from 3.

---

## What each stage does NOT change

- Stage 1: no change to openMINDS output content — same objects, same values
- Stage 2: no change to conversion behaviour — only mapping completeness and test coverage
- Stage 3: no change to openMINDS output — validation is advisory
- Stage 4: first stage that changes the output (new openMINDS objects added)
