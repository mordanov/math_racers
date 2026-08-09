"""Unit tests: structured logging redaction and field completeness."""

import json
import logging

import pytest

from infrastructure.logging import StructuredFormatter, _redact, request_id_var


@pytest.mark.unit
class TestRedaction:
    def test_redacts_password_key(self) -> None:
        result = _redact({"password": "secret123"})
        assert result["password"] == "***REDACTED***"

    def test_redacts_secret_key(self) -> None:
        result = _redact({"api_secret": "abc"})
        assert result["api_secret"] == "***REDACTED***"

    def test_redacts_token_key(self) -> None:
        result = _redact({"access_token": "tok"})
        assert result["access_token"] == "***REDACTED***"

    def test_redacts_key_field(self) -> None:
        result = _redact({"api_key": "key123"})
        assert result["api_key"] == "***REDACTED***"

    def test_preserves_non_sensitive_keys(self) -> None:
        result = _redact({"user_id": "abc", "action": "login"})
        assert result["user_id"] == "abc"
        assert result["action"] == "login"

    def test_redacts_nested_sensitive_keys(self) -> None:
        result = _redact({"database": {"password": "secret"}})
        assert result["database"]["password"] == "***REDACTED***"

    def test_passes_through_lists(self) -> None:
        result = _redact({"items": [1, 2, 3]})
        assert result["items"] == [1, 2, 3]

    def test_handles_empty_dict(self) -> None:
        assert _redact({}) == {}


@pytest.mark.unit
class TestStructuredFormatter:
    def _make_record(
        self, message: str, context: dict[str, object] | None = None
    ) -> logging.LogRecord:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        if context is not None:
            record.context = context
        return record

    def test_emits_all_required_fields(self) -> None:
        fmt = StructuredFormatter(service="backend")
        record = self._make_record("hello")
        output = json.loads(fmt.format(record))
        assert "timestamp" in output
        assert "level" in output
        assert "service" in output
        assert "request_id" in output
        assert "message" in output
        assert "context" in output

    def test_service_name_in_output(self) -> None:
        fmt = StructuredFormatter(service="worker")
        record = self._make_record("test")
        output = json.loads(fmt.format(record))
        assert output["service"] == "worker"

    def test_secret_context_keys_redacted(self) -> None:
        fmt = StructuredFormatter(service="backend")
        record = self._make_record(
            "msg", context={"api_key": "real-key", "user": "alice"}
        )
        output = json.loads(fmt.format(record))
        assert output["context"]["api_key"] == "***REDACTED***"
        assert output["context"]["user"] == "alice"

    def test_request_id_from_context_var(self) -> None:
        token = request_id_var.set("test-request-id-123")
        try:
            fmt = StructuredFormatter(service="backend")
            record = self._make_record("msg")
            output = json.loads(fmt.format(record))
            assert output["request_id"] == "test-request-id-123"
        finally:
            request_id_var.reset(token)

    def test_nil_uuid_when_no_request_id(self) -> None:
        fmt = StructuredFormatter(service="backend")
        record = self._make_record("msg")
        output = json.loads(fmt.format(record))
        assert output["request_id"] == "00000000-0000-0000-0000-000000000000"
