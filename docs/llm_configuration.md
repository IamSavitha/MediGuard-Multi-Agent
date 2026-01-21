# MediGuard: LLM Configuration (Ollama)

## Executive Summary

MediGuard uses **Ollama** as the LLM provider, enabling local model execution for enhanced privacy and control. This document outlines the Ollama configuration, model selection, and structured output support.

---

## 1. Why Ollama?

### 1.1 Benefits

- **Privacy**: Models run locally - no data leaves your infrastructure
- **Cost**: No per-token API costs - only compute resources
- **Control**: Full control over model behavior and configuration
- **Offline**: Can run without internet connectivity
- **Flexibility**: Easy to switch between different models

### 1.2 Tradeoffs

- **Infrastructure**: Requires GPU or sufficient CPU resources
- **Setup**: Need to manage model downloads and updates
- **Structured Outputs**: Some models may need JSON mode configuration (not native structured outputs like OpenAI)

---

## 2. Recommended Models

### 2.1 Primary Model (Recommended)

**Model**: `llama3.1` or `llama3.1:8b` (or larger variants)

**Why**:
- Strong reasoning capabilities
- Good JSON mode support
- Balanced performance/size
- Active development and community

**Use Cases**: 
- Document classification
- Compliance matching
- PHI detection (targeted segments)
- Verification tasks

### 2.2 Alternative Models

#### Option 1: Mistral
- **Model**: `mistral` or `mistral:7b`
- **Strengths**: Efficient, fast inference
- **Use Cases**: Classification, simple reasoning

#### Option 2: Llama 3
- **Model**: `llama3` or `llama3:8b`
- **Strengths**: Good balance of performance and speed
- **Use Cases**: General purpose agent tasks

#### Option 3: Code-focused Models (for structured outputs)
- **Model**: `deepseek-coder` or `codellama`
- **Strengths**: Excellent JSON generation
- **Use Cases**: Structured output generation

### 2.3 Model Selection Strategy

**For v1.0**: Start with `llama3.1:8b` for balance of capability and resource usage

**Scaling Options**:
- Use smaller models (7B) for simple tasks (classification)
- Use larger models (70B) for complex reasoning (compliance matching)
- Model routing based on task complexity

---

## 3. Ollama Installation & Setup

### 3.1 Installation

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

### 3.2 Pull Recommended Model

```bash
# Pull Llama 3.1 8B (recommended starting point)
ollama pull llama3.1:8b

# Or pull other models
ollama pull mistral:7b
ollama pull llama3:8b
```

### 3.3 Verify Installation

```bash
# Test model
ollama run llama3.1:8b "Hello, can you output JSON?"
```

---

## 4. Structured Outputs with Ollama

### 4.1 Challenge

Ollama models don't have native structured outputs like OpenAI's `responses.parse()` API. We need to use JSON mode with schema validation.

### 4.2 Approach

#### Method 1: JSON Mode (Recommended)

**Strategy**: Instruct model to output JSON, then validate with Pydantic

**Implementation Pattern**:
```python
from ollama import Client
from pydantic import BaseModel, ValidationError
import json

client = Client()

# Define schema
class Finding(BaseModel):
    rule_id: str
    status: Literal["pass", "fail", "needs_review"]
    confidence: float

# Prompt with JSON schema
prompt = """
You are a compliance checker. Output JSON matching this schema:
{
  "rule_id": "string",
  "status": "pass|fail|needs_review",
  "confidence": 0.0-1.0
}

Document: {redacted_doc}
Policy: {policy_chunk}

Output only valid JSON:
"""

response = client.generate(
    model="llama3.1:8b",
    prompt=prompt,
    options={
        "temperature": 0.0,  # Deterministic
        "format": "json"  # Force JSON mode if supported
    }
)

# Parse and validate
try:
    data = json.loads(response["response"])
    finding = Finding(**data)
except (json.JSONDecodeError, ValidationError) as e:
    # Fallback: retry or mark as needs_review
    finding = Finding(rule_id="unknown", status="needs_review", confidence=0.0)
```

#### Method 2: Schema in Prompt

**Strategy**: Include JSON schema explicitly in prompt

**Example Prompt**:
```
You must output JSON in this exact format:
{
  "findings": [
    {
      "rule_id": "HIPAA_SF_001",
      "status": "pass" | "fail" | "needs_review",
      "evidence_chunk_ids": ["chunk_123"],
      "confidence": 0.95
    }
  ]
}

Do not output anything else. Only JSON.
```

#### Method 3: Post-Processing

**Strategy**: Parse JSON from response, handle failures gracefully

```python
import re
import json

def extract_json(text: str) -> dict | None:
    # Try to find JSON in response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None
```

### 4.3 Validation Strategy

**Multi-Step Validation**:
1. **JSON Parsing**: Extract JSON from response
2. **Schema Validation**: Validate against Pydantic models
3. **Business Logic Validation**: Check field values make sense
4. **Fallback**: If validation fails, mark as `needs_review`

---

## 5. Model Configuration

### 5.1 Recommended Settings

```python
{
    "model": "llama3.1:8b",
    "temperature": 0.0,  # Deterministic for compliance
    "top_p": 0.9,
    "num_predict": 2048,  # Max tokens
    "format": "json",  # If supported by model
    "seed": 42  # For reproducibility
}
```

### 5.2 Task-Specific Settings

#### Classification (Low Temperature)
```python
{"temperature": 0.0, "top_p": 0.9}  # Deterministic
```

#### Compliance Matching (Structured Output)
```python
{"temperature": 0.0, "format": "json"}  # Structured
```

#### PHI Detection (Contextual)
```python
{"temperature": 0.1, "top_p": 0.95}  # Slightly creative for context
```

---

## 6. Integration with LangGraph

### 6.1 Ollama Client Setup

```python
from ollama import Client
from typing import Any

class OllamaLLM:
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.client = Client(host=base_url)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            **kwargs
        )
        return response["response"]
    
    def generate_json(self, prompt: str, schema: dict, **kwargs) -> dict:
        # Add JSON schema to prompt
        json_prompt = f"{prompt}\n\nOutput valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\nOnly output JSON, nothing else."
        
        response = self.generate(
            json_prompt,
            format="json" if "format" in kwargs else None,
            **kwargs
        )
        
        # Parse and return
        return json.loads(response)
```

### 6.2 LangGraph Node Integration

```python
from langgraph.graph import StateGraph

def compliance_matcher_node(state: State) -> State:
    # Retrieve policy chunks
    policy_chunks = state["policy_chunks"]
    
    # Build prompt
    prompt = build_compliance_prompt(state["redacted_text"], policy_chunks)
    
    # Call Ollama with JSON schema
    schema = Finding.model_json_schema()
    result = ollama_llm.generate_json(prompt, schema)
    
    # Validate with Pydantic
    findings = [Finding(**f) for f in result["findings"]]
    
    # Update state
    state["findings"] = findings
    return state
```

---

## 7. Error Handling & Fallbacks

### 7.1 JSON Parse Failures

**Strategy**: Graceful degradation

```python
try:
    finding = parse_structured_output(response)
except (JSONDecodeError, ValidationError):
    # Fallback: mark as needs_review
    finding = Finding(
        rule_id="unknown",
        status="needs_review",
        confidence=0.0,
        rationale="Unable to parse model output"
    )
```

### 7.2 Model Unavailability

**Strategy**: Retry with exponential backoff, fallback model

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_ollama_with_retry(prompt: str) -> str:
    try:
        return ollama_llm.generate(prompt)
    except Exception as e:
        # Log and retry
        logger.warning(f"Ollama call failed: {e}, retrying...")
        raise
```

### 7.3 Model Routing

**Strategy**: Use simpler models for simple tasks, complex models for complex tasks

```python
def get_model_for_task(task_type: str) -> str:
    if task_type == "classification":
        return "mistral:7b"  # Fast, efficient
    elif task_type == "compliance_matching":
        return "llama3.1:8b"  # Better reasoning
    elif task_type == "phi_detection":
        return "llama3.1:8b"  # Contextual understanding
    else:
        return "llama3.1:8b"  # Default
```

---

## 8. Performance Considerations

### 8.1 Inference Speed

**Factors**:
- Model size (7B vs 70B)
- Hardware (CPU vs GPU)
- Context length
- Temperature settings

**Optimizations**:
- Use smaller models for simple tasks
- Batch similar requests
- Cache common prompts/responses
- Use GPU acceleration when available

### 8.2 Resource Requirements

**Minimum (CPU only)**:
- 8GB RAM for 7B model
- Slower inference (may not meet latency targets)

**Recommended (GPU)**:
- 8GB+ VRAM for 7B-8B models
- 24GB+ VRAM for 70B models
- Fast inference (meets latency targets)

---

## 9. Configuration File

### 9.1 Example: `config/ollama.yaml`

```yaml
ollama:
  base_url: "http://localhost:11434"
  default_model: "llama3.1:8b"
  
  models:
    classification: "mistral:7b"
    compliance_matching: "llama3.1:8b"
    phi_detection: "llama3.1:8b"
    verification: "llama3.1:8b"
  
  settings:
    temperature: 0.0
    top_p: 0.9
    num_predict: 2048
    format: "json"
  
  retry:
    max_attempts: 3
    backoff_multiplier: 2
    max_wait: 10
```

---

## 10. Testing

### 10.1 Model Health Check

```python
def test_ollama_connection():
    client = Client()
    try:
        response = client.generate(model="llama3.1:8b", prompt="Hello")
        return True
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return False
```

### 10.2 Structured Output Test

```python
def test_json_output():
    schema = {"type": "object", "properties": {"status": {"type": "string"}}}
    result = ollama_llm.generate_json("Output JSON with status field", schema)
    assert "status" in result
```

---

## 11. Migration from OpenAI (Future Reference)

If migrating from OpenAI to Ollama:

1. Replace `OpenAI()` client with `Ollama()` client
2. Change API calls from `client.chat.completions.create()` to `client.generate()`
3. Replace native structured outputs with JSON mode + Pydantic validation
4. Update error handling for different error types
5. Adjust prompts for model-specific formatting

---

## 12. Next Steps

- [ ] Install Ollama and pull recommended models
- [ ] Create Ollama client wrapper
- [ ] Implement JSON mode parsing with Pydantic validation
- [ ] Test structured outputs with compliance schemas
- [ ] Configure model routing for different tasks
- [ ] Set up monitoring for model performance

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Draft - Awaiting Review
