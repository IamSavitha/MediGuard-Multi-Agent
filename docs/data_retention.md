# MediGuard: Data Retention & Controls Strategy

## Executive Summary

This document defines MediGuard's data retention policy and data controls strategy. Since we're using Ollama (local LLM) instead of OpenAI, we adapt the original plan to focus on local data handling, ephemeral processing, and compliance-safe data practices.

---

## 1. Data Retention Principles

### 1.1 Core Principles

- **Ephemeral Processing**: Patient documents processed in-memory; stored only if org policy allows
- **Minimal Retention**: Retain only what's necessary for compliance/audit
- **PHI-Free Logs**: No PHI in logs; use hashes/IDs instead
- **Policy Alignment**: Retention aligned with organizational policy and regulations
- **Audit Requirements**: Retain enough for audit trails without PHI

### 1.2 Tradeoffs

**Lower Retention**:
- ✅ Reduced compliance risk
- ✅ Less storage cost
- ✅ Faster cleanup
- ❌ Reduced observability
- ❌ Harder incident response

**Higher Retention**:
- ✅ Better observability
- ✅ Easier incident response
- ✅ More debugging capability
- ❌ Higher compliance risk
- ❌ More storage cost

**Decision**: Minimal retention with PHI-free metadata only.

---

## 2. Data Categories & Retention

### 2.1 Raw Documents (PHI-Containing)

**Type**: Original patient documents submitted by users

**Retention Policy**:
- **v1.0 Default**: **Ephemeral (no persistence)**
  - Processed in-memory only
  - Deleted immediately after redaction
  - Not stored in database or file system

**Exception**: If organizational policy requires:
- Encrypted storage with access controls
- Automatic deletion after processing
- Audit logging of storage/access

**Rationale**: Maximum privacy, minimal risk

### 2.2 Redacted Documents

**Type**: Documents with PHI replaced by placeholders

**Retention Policy**:
- **Default**: Retain for **30 days** (configurable)
  - Allows reprocessing/review if needed
  - Automatic deletion after retention period
  - Stored with encryption at rest

**Access**: Authorized personnel only, logged

**Rationale**: Balance utility (reprocessing) with privacy

### 2.3 Compliance Findings (JSON)

**Type**: Structured compliance results (no PHI)

**Retention Policy**:
- **Default**: Retain for **1 year** (configurable)
  - Audit trail requirement
  - Compliance reporting
  - Trend analysis (aggregated)

**Access**: Authorized personnel, audit logs

**Rationale**: Audit requirements without PHI exposure

### 2.4 Audit Reports

**Type**: Human-readable reports (redacted content only)

**Retention Policy**:
- **Default**: Retain for **1 year** (configurable)
  - Same as compliance findings
  - Download/export capability for long-term storage (org responsibility)

**Access**: Authorized personnel, audit logs

**Rationale**: Audit trail without PHI

### 2.5 Audit Logs (PHI-Free Metadata)

**Type**: System logs, access logs, processing events

**Retention Policy**:
- **Default**: Retain for **90 days** (configurable)
  - Incident investigation
  - Performance monitoring
  - Compliance reporting

**Content**: No PHI, only metadata:
- Run IDs, document IDs
- Timestamps, status
- Counts, error codes
- User IDs, API keys (hashed)

**Rationale**: Operational needs without PHI risk

### 2.6 Policy Chunks (Non-PHI)

**Type**: Embedded policy documents from Pinecone

**Retention Policy**:
- **Permanent** (until policy updated)
  - Not PHI, safe to retain
  - Versioned for historical reference
  - Deleted only when deprecated

**Rationale**: Policies are not PHI, needed for retrieval

### 2.7 Model Inputs/Outputs (Ollama)

**Type**: Redacted documents sent to Ollama, model responses

**Retention Policy**:
- **v1.0 Default**: **Ephemeral (no persistence)**
  - Local processing, no external API
  - No persistent storage of model I/O
  - Logged only as metadata (request ID, timestamp)

**Future**: If debugging needed:
- Store redacted examples (no PHI)
- Hash-based identifiers
- Automatic cleanup

**Rationale**: Local processing = no external storage concerns

---

## 3. Data Storage Locations

### 3.1 In-Memory (Ephemeral)

**Stored**:
- Raw documents during processing
- Intermediate state (before redaction)
- Model inputs/outputs (during processing)

**Retention**: Until processing complete, then deleted

**Access**: Process only, no external access

### 3.2 Database (PostgreSQL)

**Stored**:
- Compliance findings (JSON)
- Redaction summaries (metadata)
- Audit logs (PHI-free)
- Run metadata (IDs, timestamps)

**Retention**: Per category (see Section 2)

**Access**: API queries, authorized only

**Encryption**: At rest (TDE or application-level)

### 3.3 File System / Object Storage

**Stored**:
- Redacted documents (if retention enabled)
- Audit reports (if retained)

**Retention**: Per category (see Section 2)

**Access**: API downloads, authorized only

**Encryption**: At rest

### 3.4 Pinecone (Vector DB)

**Stored**:
- Policy chunks only (non-PHI)
- Policy metadata
- Embeddings

**Retention**: Permanent (until deprecated)

**Access**: Retrieval agent only

**No PHI**: Design prevents PHI in Pinecone

### 3.5 Ollama (Local LLM)

**Stored**:
- Model weights (local)
- No user data persisted
- No conversation history by default

**Retention**: Model weights: permanent, no user data stored

**Access**: Local API only

**No PHI**: Only redacted documents sent

---

## 4. Ollama-Specific Data Controls

### 4.1 No External API

**Benefit**: 
- No data sent to external services
- Complete control over data
- No third-party data retention concerns

**Controls**:
- Ollama runs locally
- No internet connection required for inference
- No external logging/analytics

### 4.2 Model Input/Output

**Input**: Only redacted documents
- Pre-send validation (check for PHI)
- No raw documents sent

**Output**: Model responses (structured JSON)
- Post-response validation (check for PHI)
- Sanitize before use

**Storage**: No persistent storage of I/O by default
- Ephemeral during processing
- Logged only as metadata (request ID, timestamp, status)

### 4.3 Model Updates

**When**: Model weights updated (pulling new model versions)

**How**: Manual or automated (configurable)

**Controls**:
- Version tracking
- Rollback capability
- No impact on user data (models are separate)

### 4.4 Local Analytics (Optional)

**If Enabled**:
- Aggregate metrics only (no PHI)
- Request counts, success rates
- Processing time statistics
- Error rates (generic)

**Storage**: Local only, no external transmission

---

## 5. Data Deletion & Cleanup

### 5.1 Automatic Deletion

**Implementation**:
- Scheduled cleanup jobs (daily)
- Retention period checks
- Automatic deletion after retention period

**Example**:
```python
# Scheduled job: daily cleanup
def cleanup_expired_data():
    """Delete data past retention period"""
    # Delete expired redacted documents
    delete_expired_redacted_documents(retention_days=30)
    
    # Delete expired compliance findings (if org policy allows)
    # delete_expired_findings(retention_days=365)  # Typically keep for audit
    
    # Delete expired audit logs
    delete_expired_audit_logs(retention_days=90)
```

### 5.2 Manual Deletion

**User-Initiated**:
- Users can delete their own documents (if stored)
- Compliance officer can delete documents per policy
- Admin can delete for incident response

**Access Control**: RBAC-based, logged

### 5.3 Deletion Verification

**After Deletion**:
- Verify deletion completed
- Log deletion event (PHI-free metadata)
- Confirm no orphaned references

---

## 6. Data Access Controls

### 6.1 Access Principles

- **Least Privilege**: Users access only what they need
- **Role-Based**: RBAC controls access
- **Tenant Isolation**: Multi-tenant separation
- **Audit Logging**: All access logged

### 6.2 Access Levels

**User Roles**:
- **Submitter**: Can submit documents, view own results
- **Reviewer**: Can review compliance findings, audit reports
- **Compliance Officer**: Can access all findings, reports, audit logs
- **Admin**: Full access, system configuration

**Tenant Isolation**:
- Users only see data from their organization
- API keys scoped to tenant
- Database queries filtered by tenant_id

### 6.3 Access Logging

**Logged Events**:
- Document submission (who, when, document_id)
- Result retrieval (who, when, run_id)
- Report download (who, when, report_id)
- Admin actions (who, what, when)

**No PHI in Access Logs**: Only metadata (IDs, timestamps)

---

## 7. Data Retention Configuration

### 7.1 Configuration File

**Example**: `config/retention.yaml`

```yaml
retention:
  # Raw documents (PHI-containing)
  raw_documents:
    enabled: false  # Ephemeral by default
    days: 0  # Not used if disabled
  
  # Redacted documents
  redacted_documents:
    enabled: true
    days: 30
    encryption_at_rest: true
  
  # Compliance findings
  compliance_findings:
    enabled: true
    days: 365
    encryption_at_rest: true
  
  # Audit reports
  audit_reports:
    enabled: true
    days: 365
    encryption_at_rest: true
  
  # Audit logs (PHI-free)
  audit_logs:
    enabled: true
    days: 90
    encryption_at_rest: true
  
  # Cleanup schedule
  cleanup:
    schedule: "daily"  # daily, weekly, etc.
    time: "02:00"  # 2 AM
```

### 7.2 Per-Organization Override

**Capability**: Organizations can override defaults

**Implementation**:
- Organization-level retention policy
- Stored in database (org_id → retention_config)
- Applied when processing documents for that org

**Use Case**: Different compliance requirements per organization

---

## 8. Compliance Considerations

### 8.1 HIPAA Considerations

**Minimum Necessary**: 
- Retain only what's necessary for compliance/audit
- No PHI in logs/analytics
- Automatic deletion after retention period

**Access Controls**:
- Role-based access
- Audit logging of access
- Encryption at rest

### 8.2 Audit Requirements

**What's Needed**:
- Compliance findings (for reporting)
- Audit logs (for incident investigation)
- Access logs (for access tracking)

**What's NOT Needed**:
- Raw documents (after processing)
- PHI values
- Model inputs/outputs (after processing)

**Balance**: Retain enough for audit without PHI exposure

---

## 9. Success Criteria for Step 6

This data retention strategy is complete when:
- [x] Retention policies are defined for all data categories
- [x] Ollama-specific controls are documented
- [x] Data deletion and cleanup procedures are specified
- [x] Access controls are defined
- [x] Configuration options are documented
- [x] Compliance considerations are addressed

---

## 10. Next Steps

After data retention approval, proceed to:
- **Step 7**: Define measurable success metrics
- **Step 9**: Choose stack and repo layout (start implementation)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Draft - Awaiting Review
