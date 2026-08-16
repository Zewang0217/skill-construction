"""Basic tests for core functionality."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from env_buddy import core


def test_set_get():
    core.set_var("TEST_VAR_123", "hello")
    assert core.get_var("TEST_VAR_123") == "hello"
    core.delete_var("TEST_VAR_123")


def test_export_dotenv():
    os.environ["FB_TEST"] = "a\"b"
    out = core.export_env(format="dotenv", prefix="FB_")
    assert 'FB_TEST="a\\"b"' in out


def test_import_sanitized():
    core.import_env('BAD_VAR="$(touch /tmp/pwned)"', sanitize=True)
    assert "BAD_VAR" not in os.environ
    core.import_env('GOOD_VAR="safe"', sanitize=True)
    assert os.environ.get("GOOD_VAR") == "safe"
    core.delete_var("GOOD_VAR")


def test_import_unsafe_raw():
    # 用户显式 --no-sanitize 时应能接受任意值（测试边界情况）
    core.import_env('RAW_VAR="echo hi"', sanitize=False)
    assert os.environ.get("RAW_VAR") == "echo hi"
    core.delete_var("RAW_VAR")