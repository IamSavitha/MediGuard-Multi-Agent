"""
Unit tests for gold set validation
"""
import json
from pathlib import Path
import pytest


def test_label_file_structure():
    """Test that label files have correct structure"""
    labels_dir = Path(__file__).parent.parent.parent / "data" / "gold_set" / "labels"
    
    for label_file in labels_dir.glob("*.labels.json"):
        with open(label_file) as f:
            data = json.load(f)
        
        # Check required fields
        assert "schema_version" in data
        assert "document_id" in data
        assert "doc_type" in data
        assert "jurisdiction" in data
        assert "phi_spans" in data
        assert "compliance_expected" in data
        
        # Check PHI spans structure
        for span in data["phi_spans"]:
            assert "phi_type" in span
            assert "start" in span
            assert "end" in span
            assert "text" in span
            assert isinstance(span["start"], int)
            assert isinstance(span["end"], int)
            assert span["start"] < span["end"]


def test_phi_spans_match_documents():
    """Test that PHI spans match actual document content"""
    docs_dir = Path(__file__).parent.parent.parent / "data" / "gold_set" / "documents"
    labels_dir = Path(__file__).parent.parent.parent / "data" / "gold_set" / "labels"
    
    for label_file in labels_dir.glob("*.labels.json"):
        with open(label_file) as f:
            label_data = json.load(f)
        
        doc_id = label_data["document_id"]
        doc_file = docs_dir / f"{doc_id}.txt"
        
        if doc_file.exists():
            doc_text = doc_file.read_text()
            
            # Verify each PHI span matches document content
            for span in label_data["phi_spans"]:
                start = span["start"]
                end = span["end"]
                expected_text = span["text"]
                actual_text = doc_text[start:end]
                
                assert actual_text == expected_text, (
                    f"Mismatch in {doc_id}: expected '{expected_text}' "
                    f"at [{start}:{end}], got '{actual_text}'"
                )
