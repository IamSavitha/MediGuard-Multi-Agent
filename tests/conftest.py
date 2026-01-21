"""
Pytest configuration and fixtures
"""
import pytest
import os
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent.parent / "data" / "gold_set"


@pytest.fixture
def sample_document():
    """Sample document text for testing"""
    return """PROGRESS NOTE
Patient: John Smith
DOB: 01/15/1985
MRN: MRN-123456
Phone: (555) 123-4567

HPI:
Patient reports intermittent chest pain for 2 days.

Assessment:
Rule out ACS.

Plan:
EKG, troponin, follow up in 1 week."""


@pytest.fixture
def sample_phi_spans():
    """Sample PHI spans for testing"""
    return [
        {"phi_type": "patient_name", "start": 23, "end": 33, "text": "John Smith"},
        {"phi_type": "date", "start": 39, "end": 49, "text": "01/15/1985"},
        {"phi_type": "mrn", "start": 55, "end": 65, "text": "MRN-123456"},
        {"phi_type": "phone", "start": 73, "end": 87, "text": "(555) 123-4567"},
    ]
