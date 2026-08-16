"""Custom exceptions for the API client wrapper."""


class ClientError(Exception):
    """Raised when a request fails after all retries, or other client-level errors."""


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required fields."""