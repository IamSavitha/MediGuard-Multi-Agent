import json
import re
from dataclasses import dataclass
from pathlib import Path


GOLD_SET_DIR = Path(__file__).resolve().parents[2] / "data" / "gold_set"
DOCS_DIR = GOLD_SET_DIR / "documents"
LABELS_DIR = GOLD_SET_DIR / "labels"


@dataclass(frozen=True)
class Span:
    phi_type: str
    start: int
    end: int
    text: str


PHONE_RE = re.compile(r"\b(?:\(\d{3}\)\s*\d{3}-\d{4}|\d{3}[.-]\d{3}[.-]\d{4})\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
DATE_RE = re.compile(r"\b(?:\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\b")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_spans(label_obj: dict) -> list[Span]:
    spans = []
    for s in label_obj.get("phi_spans", []):
        spans.append(Span(phi_type=s["phi_type"], start=s["start"], end=s["end"], text=s["text"]))
    return spans


def validate_spans(text: str, spans: list[Span]) -> list[str]:
    errors: list[str] = []
    for s in spans:
        if not (0 <= s.start <= s.end <= len(text)):
            errors.append(f"Span out of bounds: {s}")
            continue
        actual = text[s.start : s.end]
        if actual != s.text:
            errors.append(
                f"Span text mismatch for {s.phi_type} @[{s.start},{s.end}): "
                f"expected={s.text!r} actual={actual!r}"
            )
    # overlap check
    sorted_spans = sorted(spans, key=lambda x: (x.start, x.end))
    for i in range(1, len(sorted_spans)):
        prev = sorted_spans[i - 1]
        cur = sorted_spans[i]
        if cur.start < prev.end:
            errors.append(f"Overlapping spans: {prev} overlaps {cur}")
    return errors


def baseline_detect(text: str) -> list[Span]:
    """
    Baseline PHI detector (rules only). This is intentionally simple:
    it catches easy identifiers but will miss contextual PHI (names in narrative).
    """
    spans: list[Span] = []
    for m in PHONE_RE.finditer(text):
        spans.append(Span(phi_type="phone", start=m.start(), end=m.end(), text=m.group(0)))
    for m in EMAIL_RE.finditer(text):
        spans.append(Span(phi_type="email", start=m.start(), end=m.end(), text=m.group(0)))
    for m in SSN_RE.finditer(text):
        spans.append(Span(phi_type="ssn", start=m.start(), end=m.end(), text=m.group(0)))
    for m in DATE_RE.finditer(text):
        spans.append(Span(phi_type="date", start=m.start(), end=m.end(), text=m.group(0)))
    return sorted(spans, key=lambda x: (x.start, x.end))


def span_iou(a: Span, b: Span) -> float:
    inter = max(0, min(a.end, b.end) - max(a.start, b.start))
    union = max(a.end, b.end) - min(a.start, b.start)
    return inter / union if union else 0.0


def score_spans(gold: list[Span], pred: list[Span], iou_threshold: float = 0.5) -> dict:
    """
    Greedy matching by IoU. For this starter harness we don't require phi_type to match.
    (We’ll tighten this once we implement typed placeholders and category mapping.)
    """
    gold_used = [False] * len(gold)
    pred_used = [False] * len(pred)

    tp = 0
    for i, p in enumerate(pred):
        best_j = None
        best_iou = 0.0
        for j, g in enumerate(gold):
            if gold_used[j]:
                continue
            iou = span_iou(p, g)
            if iou > best_iou:
                best_iou = iou
                best_j = j
        if best_j is not None and best_iou >= iou_threshold:
            tp += 1
            gold_used[best_j] = True
            pred_used[i] = True

    fp = sum(1 for used in pred_used if not used)
    fn = sum(1 for used in gold_used if not used)

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 1.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def main() -> int:
    label_files = sorted(LABELS_DIR.glob("*.labels.json"))
    if not label_files:
        print(f"No labels found in {LABELS_DIR}")
        return 1

    all_scores = {"tp": 0, "fp": 0, "fn": 0}
    had_errors = False

    for lf in label_files:
        label = load_json(lf)
        doc_id = label["document_id"]
        doc_path = DOCS_DIR / f"{doc_id}.txt"
        text = load_text(doc_path)

        gold = load_spans(label)
        errors = validate_spans(text, gold)
        if errors:
            had_errors = True
            print(f"\n[ERROR] {doc_id}: label validation failed")
            for e in errors:
                print(f"  - {e}")
            continue

        pred = baseline_detect(text)
        score = score_spans(gold, pred, iou_threshold=0.5)
        print(
            f"{doc_id}: gold={len(gold)} pred={len(pred)} "
            f"P={score['precision']:.4f} R={score['recall']:.4f} F1={score['f1']:.4f}"
        )

        all_scores["tp"] += score["tp"]
        all_scores["fp"] += score["fp"]
        all_scores["fn"] += score["fn"]

    if had_errors:
        print("\nFix label errors above before trusting metrics.")
        return 2

    tp, fp, fn = all_scores["tp"], all_scores["fp"], all_scores["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 1.0
    print("\n=== Baseline (rules-only) PHI span metrics ===")
    print(f"TP={tp} FP={fp} FN={fn}")
    print(f"Precision={precision:.4f} Recall={recall:.4f} F1={f1:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

