# MediGuard: Success Metrics Specification

## Executive Summary

This document defines measurable success metrics for MediGuard. These metrics allow us to prove impact, tune prompts/retrieval, and demonstrate value. Without metrics, we can't prove impact or improve accuracy.

---

## 1. Metrics Philosophy

### 1.1 Why Metrics Matter

- **Prove Impact**: "50% time reduction" vs "faster"
- **Tune System**: Data-driven optimization vs guesswork
- **Measure Progress**: Baseline vs improved
- **Demonstrate Value**: Quantifiable benefits for stakeholders

### 1.2 Metrics Categories

1. **Efficiency Metrics**: Time/cost savings
2. **Accuracy Metrics**: Correctness of compliance matching
3. **Safety Metrics**: PHI leakage, false positives/negatives
4. **Operational Metrics**: Latency, throughput, reliability

---

## 2. Efficiency Metrics

### 2.1 Audit Time Reduction

**Metric**: Time from document submission to final decision

**Baseline**: Manual audit time per document
- **Measurement**: Average time for human compliance officer to review document
- **Example**: 30 minutes per document (baseline)

**Target**: **50% reduction** in audit time
- **Target Value**: 15 minutes or less per document (assisted)
- **Measurement**: Time from API submission to routing decision

**Calculation**:
```python
time_reduction_pct = ((baseline_time - assisted_time) / baseline_time) * 100
```

**Measurement Method**:
- Track timestamps: `submission_time`, `processing_complete_time`, `decision_time`
- Calculate: `processing_time = decision_time - submission_time`
- Compare to baseline: manual average time

### 2.2 Cost per Document

**Metric**: Processing cost per document

**Components**:
- Compute resources (Ollama local inference)
- Storage (if retention enabled)
- Infrastructure overhead

**Target**: Track and optimize (cost reduction over time)

**Calculation**:
```python
cost_per_document = (
    compute_cost + 
    storage_cost + 
    infrastructure_overhead
) / document_count
```

**Note**: Using Ollama (local) reduces per-token API costs to compute costs only

### 2.3 Throughput

**Metric**: Documents processed per hour

**Target**: **100 documents/hour per instance**

**Measurement**:
- Count successful completions per hour
- Track peak and average throughput

**Calculation**:
```python
throughput = documents_processed / time_window_hours
```

---

## 3. Accuracy Metrics

### 3.1 Compliance Matching Accuracy

**Metric**: **92% accuracy** in compliance matching

**Definition**: 
- **Precision**: % of flagged issues that are actual violations
- **Recall**: % of actual violations that are detected
- **Accuracy**: Overall correctness (can use F1 score or exact-match rate)

**Measurement**: Against labeled gold set (synthetic documents)

**Target Values**:
- **Precision**: ≥ 90% (few false positives)
- **Recall**: ≥ 94% (catch most violations)
- **F1 Score**: ≥ 92% (balanced precision/recall)
- **Exact-Match Rate**: ≥ 92% (exact compliance status match)

**Calculation**:
```python
# Precision: True Positives / (True Positives + False Positives)
precision = TP / (TP + FP)

# Recall: True Positives / (True Positives + False Negatives)
recall = TP / (TP + FN)

# F1 Score: Harmonic mean of precision and recall
f1 = 2 * (precision * recall) / (precision + recall)

# Exact-Match Rate: % of documents with exact status match
exact_match_rate = exact_matches / total_documents
```

**By Rule Type**:
- Track accuracy per rule (HIPAA_SF_001, INT_DOC_001, etc.)
- Identify rules with lower accuracy for improvement

### 3.2 Finding-Level Accuracy

**Metric**: Accuracy at the finding level (not just document level)

**Definition**: Per-finding correctness (rule_id, status, evidence)

**Target**: ≥ 90% finding-level accuracy

**Measurement**: Compare findings to gold set labels

**Calculation**:
```python
finding_accuracy = correct_findings / total_findings
```

### 3.3 Evidence Quality

**Metric**: % of findings with correct evidence chunk_ids

**Definition**: Evidence chunk_id correctly references relevant policy

**Target**: ≥ 95% evidence correctness

**Measurement**: Manual review or automated checks against gold set

---

## 4. Safety Metrics

### 4.1 PHI Leakage Rate

**Metric**: **< 0.1%** leakage rate

**Definition**: % of documents where redacted output contains PHI

**Measurement**: 
- Post-redaction validation (leakage check)
- Automated PHI detection on redacted output
- Manual spot-checks on sample

**Calculation**:
```python
leakage_rate = (documents_with_phi_in_output / total_documents) * 100
```

**Target**: < 0.1% (1 in 1000 documents)

**Severity**: Critical - any PHI leakage is a compliance violation

### 4.2 False Positive Rate (Redaction)

**Metric**: **< 5%** false positive rate

**Definition**: % of non-PHI text incorrectly redacted

**Measurement**: 
- Compare redactions to gold set labels
- Manual review of false positives

**Calculation**:
```python
false_positive_rate = (false_positives / non_phi_text_instances) * 100
```

**Target**: < 5%

**Example**: Medication names incorrectly tagged as patient names

### 4.3 False Negative Rate (Redaction)

**Metric**: **< 2%** false negative rate

**Definition**: % of PHI that is missed (not redacted)

**Measurement**: 
- Compare redactions to gold set labels
- Manual review of false negatives

**Calculation**:
```python
false_negative_rate = (missed_phi / total_phi_instances) * 100
```

**Target**: < 2%

**Severity**: High - missed PHI is a compliance risk

### 4.4 False Positive Rate (Compliance)

**Metric**: **< 5%** false positive rate

**Definition**: % of compliant documents incorrectly flagged as non-compliant

**Measurement**: Compare to gold set labels

**Calculation**:
```python
false_positive_rate = (compliant_docs_flagged_as_fail / compliant_docs) * 100
```

**Target**: < 5%

**Impact**: Low (safe to over-flag for review)

### 4.5 False Negative Rate (Compliance)

**Metric**: **< 8%** false negative rate

**Definition**: % of non-compliant documents missed (incorrectly marked as compliant)

**Measurement**: Compare to gold set labels

**Calculation**:
```python
false_negative_rate = (non_compliant_docs_missed / non_compliant_docs) * 100
```

**Target**: < 8%

**Severity**: High - missed violations are compliance risk

---

## 5. Operational Metrics

### 5.1 Processing Latency

**Metric**: **< 30 seconds** per document (95th percentile)

**Definition**: Time from document submission to compliance result

**Measurement**:
- Track: `submission_time` → `result_ready_time`
- Calculate: `latency = result_ready_time - submission_time`
- Report: p50, p95, p99 percentiles

**Target**: 
- **p50 (median)**: < 15 seconds
- **p95**: < 30 seconds
- **p99**: < 60 seconds

**Components**:
- Document parsing
- PHI detection and redaction
- Policy retrieval
- Compliance matching
- Verification

### 5.2 System Reliability

**Metric**: Uptime and error rates

**Definitions**:
- **Uptime**: % of time system is available
- **Error Rate**: % of requests that fail

**Target**:
- **Uptime**: ≥ 99.5% (SLA)
- **Error Rate**: < 1%

**Measurement**:
```python
uptime = (uptime_seconds / total_seconds) * 100
error_rate = (failed_requests / total_requests) * 100
```

### 5.3 Queue/Backlog

**Metric**: Queue depth and wait time

**Target**: 
- Average queue depth: < 10 documents
- Average wait time: < 1 minute

**Measurement**:
- Track queue depth over time
- Track wait time from submission to processing start

---

## 6. Measurement Methodology

### 6.1 Gold Set (Labeled Dataset)

**Requirement**: 100-500 synthetic documents with known:
- PHI spans (exact locations)
- Compliance outcomes (pass/fail per rule)
- Expected redactions
- Expected findings

**Purpose**:
- Regression testing
- Accuracy measurement
- System tuning

**Maintenance**:
- Regular updates as rules change
- Adversarial examples (edge cases)
- Realistic synthetic data

### 6.2 Evaluation Process

**Automated**:
- Run gold set through pipeline
- Compare outputs to labels
- Calculate metrics automatically

**Manual**:
- Spot-checks on random samples
- Review of edge cases
- Expert validation of findings

### 6.3 Baseline Measurement

**Before MediGuard**:
- Measure manual audit time
- Measure manual error rates
- Establish baseline metrics

**After MediGuard**:
- Compare to baseline
- Calculate improvement
- Track trends over time

---

## 7. Metrics Dashboard

### 7.1 Real-Time Metrics

**Dashboard Shows**:
- Current throughput (documents/hour)
- Average latency (current hour)
- Error rate (current hour)
- Queue depth

**Update Frequency**: Real-time (streaming)

### 7.2 Historical Metrics

**Dashboard Shows**:
- Throughput over time (daily/weekly)
- Latency trends (percentiles)
- Accuracy over time (weekly/monthly)
- Error rate trends

**Time Range**: Configurable (7 days, 30 days, etc.)

### 7.3 Alerting

**Alerts Trigger On**:
- PHI leakage detected (critical)
- Accuracy drops below threshold (warning)
- Latency exceeds threshold (warning)
- Error rate spikes (critical)
- System down (critical)

---

## 8. Reporting

### 8.1 Weekly Reports

**Content**:
- Summary statistics (throughput, accuracy, latency)
- Top issues (rules with low accuracy)
- Improvement trends
- Incident summary

### 8.2 Monthly Reports

**Content**:
- Efficiency metrics (time reduction)
- Accuracy trends (precision, recall, F1)
- Safety metrics (leakage rate, false positives/negatives)
- Operational metrics (reliability, throughput)
- Recommendations for improvement

---

## 9. Success Criteria for Step 7

This metrics specification is complete when:
- [x] Efficiency metrics are defined (time reduction, cost)
- [x] Accuracy metrics are defined (precision, recall, F1)
- [x] Safety metrics are defined (leakage, false positives/negatives)
- [x] Operational metrics are defined (latency, throughput, reliability)
- [x] Measurement methodology is specified
- [x] Targets are set for each metric

---

## 10. Next Steps

After metrics approval, proceed to:
- **Step 8**: Create labeled "gold set" (synthetic) + baseline process
- **Step 48**: Build full evaluation harness (automated, repeatable)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Draft - Awaiting Review
