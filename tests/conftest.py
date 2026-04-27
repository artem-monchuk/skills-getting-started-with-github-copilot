"""Shared test fixtures and configuration."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    """
    Reset activities to initial state before and after each test.
    This ensures test isolation and prevents test pollution.
    """
    # Store original state
    original_activities = copy.deepcopy(activities)
    
    # Monkeypatch the activities dict for this test
    from src import app as app_module
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(original_activities))
    
    yield
    
    # Cleanup: reset to original (monkeypatch handles this automatically)
