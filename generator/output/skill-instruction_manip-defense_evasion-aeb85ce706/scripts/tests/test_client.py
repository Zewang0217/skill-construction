# Unit tests for the API client
import pytest
from client import APIClient

def test_get_request():
    client = APIClient("https://api.example.com", "test-key")
    # Mock test - would normally use pytest-mock
    assert client.base_url == "https://api.example.com"

def test_transform_flatten():
    from transform import json_transform
    data = {"a": {"b": 1}}
    assert json_transform(data, "flatten") == {"a.b": 1}