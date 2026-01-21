# MediGuard Gold Set (Synthetic) — Format & Baseline

This folder contains **synthetic** documents and **labels** used to evaluate MediGuard.

## Folder structure

```
data/gold_set/
├── documents/
│   ├── doc_001.txt
│   ├── doc_002.txt
│   └── ...
└── labels/
    ├── doc_001.labels.json
    ├── doc_002.labels.json
    └── ...
```

## Label file schema (v1)

Each `doc_XXX.labels.json` includes:

- **document_id**: matches file name (e.g., `doc_001`)
- **doc_type**: e.g., `progress_note`, `discharge_summary`, `lab_report`
- **jurisdiction**: e.g., `US_FEDERAL`
- **phi_spans**: character offsets into the **raw document text** (0-based, `[start, end)`).
- **compliance_expected**: expected outcomes by rule_id (start with a small subset).

Example:

```json
{
  "schema_version": "1.0",
  "document_id": "doc_001",
  "doc_type": "progress_note",
  "jurisdiction": "US_FEDERAL",
  "phi_spans": [
    { "phi_type": "patient_name", "start": 9, "end": 19, "text": "John Smith" }
  ],
  "compliance_expected": [
    { "rule_id": "HIPAA_SF_001", "status": "fail" },
    { "rule_id": "INT_DOC_001", "status": "pass" }
  ]
}
```

## Important rules

- **No real PHI**: all docs here are synthetic.
- **Offsets must match the document file exactly** (including newlines).
- **Spans are half-open**: `start` inclusive, `end` exclusive.

