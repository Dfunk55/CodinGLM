"""Tests for configuration module."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from codinglm.config import Config, ContextCompressionConfig


@pytest.fixture(autouse=True)
def clear_config_env(monkeypatch):
    """Remove environment variables that could influence config defaults."""
    keys = (
        "Z_AI_API_KEY",
        "ZAI_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CODINGLM_MODEL",
        "GLM_CODER_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CODINGLM_BASE_URL",
        "GLM_CODER_BASE_URL",
        "ANTHROPIC_BASE_URL",
        "Z_AI_BASE_URL",
        "CODINGLM_TIMEOUT_MS",
        "GLM_CODER_TIMEOUT_MS",
        "API_TIMEOUT_MS",
        "ANTHROPIC_TIMEOUT_MS",
    )
    for key in keys:
        monkeypatch.delenv(key, raising=False)


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    assert config.model == "glm-4.6"
    assert config.temperature == 0.7
    assert config.maxTokens == 8192
    assert config.apiBase == "https://api.z.ai/api/anthropic"
    assert config.apiTimeoutMs == 600000


def test_config_load_nonexistent():
    """Test loading config when no file exists."""
    config = Config.load(Path("/nonexistent/path"))
    assert config.model == "glm-4.6"


def test_config_get_api_key_missing():
    """Test error when API key is not set."""
    config = Config()
    with pytest.raises(ValueError):
        config.get_api_key()


def test_config_env_var_priority(monkeypatch):
    """Config should prefer the modern Z_AI_API_KEY over legacy names."""
    monkeypatch.setenv("ZAI_API_KEY", "legacy-key")
    monkeypatch.setenv("Z_AI_API_KEY", "primary-key")
    config = Config.load(Path("/nonexistent/path"))
    assert config.apiKey == "primary-key"
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.delenv("Z_AI_API_KEY", raising=False)


def test_config_model_from_codinglm_env(monkeypatch):
    """Config should honour the new CODINGLM_MODEL environment variable."""
    monkeypatch.setenv("CODINGLM_MODEL", "glm-4-flash")
    config = Config.load(Path("/nonexistent/path"))
    assert config.model == "glm-4-flash"
    monkeypatch.delenv("CODINGLM_MODEL", raising=False)


def test_config_model_from_anthropic_env(monkeypatch):
    """Config should honour Claude Code style model environment variables."""
    monkeypatch.delenv("CODINGLM_MODEL", raising=False)
    monkeypatch.delenv("GLM_CODER_MODEL", raising=False)
    monkeypatch.setenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "glm-4.5-air")
    config = Config.load(Path("/nonexistent/path"))
    assert config.model == "glm-4.5-air"
    monkeypatch.delenv("ANTHROPIC_DEFAULT_SONNET_MODEL", raising=False)


def test_config_base_url_override(monkeypatch):
    """Config should allow overriding the API base URL."""
    monkeypatch.setenv("CODINGLM_BASE_URL", "https://example.com/custom")
    config = Config.load(Path("/nonexistent/path"))
    assert config.apiBase == "https://example.com/custom"
    monkeypatch.delenv("CODINGLM_BASE_URL", raising=False)


def test_config_timeout_override(monkeypatch):
    """Config should parse timeout overrides from environment."""
    monkeypatch.setenv("CODINGLM_TIMEOUT_MS", "120000")
    config = Config.load(Path("/nonexistent/path"))
    assert config.apiTimeoutMs == 120000
    monkeypatch.delenv("CODINGLM_TIMEOUT_MS", raising=False)


# ------------------------------------------------------------------ #
# Context Compression Config Validation Tests
# ------------------------------------------------------------------ #


def test_compression_config_defaults():
    """Test default compression configuration values (maximized for GLM-4.6 subscription users)."""
    config = ContextCompressionConfig()
    assert config.enabled is True
    assert config.maxContextTokens == 185000
    assert config.targetContextTokens == 165000
    assert config.preserveRecentMessages == 15
    assert config.summaryMaxTokens == 2000


def test_compression_config_preserve_recent_minimum():
    """Test that preserveRecentMessages must be at least 1."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(preserveRecentMessages=0)
    assert "preserveRecentMessages must be at least 1" in str(exc_info.value)


def test_compression_config_target_less_than_max():
    """Test that targetContextTokens must be less than maxContextTokens."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(
            maxContextTokens=10000,
            targetContextTokens=15000,
        )
    assert "targetContextTokens" in str(exc_info.value)
    assert "must be less than" in str(exc_info.value)


def test_compression_config_target_equal_max():
    """Test that targetContextTokens cannot equal maxContextTokens."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(
            maxContextTokens=10000,
            targetContextTokens=10000,
        )
    assert "targetContextTokens" in str(exc_info.value)


def test_compression_config_max_tokens_positive():
    """Test that maxContextTokens must be positive."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(maxContextTokens=0)
    assert "maxContextTokens must be greater than 0" in str(exc_info.value)


def test_compression_config_target_tokens_positive():
    """Test that targetContextTokens must be positive."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(targetContextTokens=-100)
    assert "targetContextTokens must be greater than 0" in str(exc_info.value)


def test_compression_config_summary_tokens_positive():
    """Test that summaryMaxTokens must be positive."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(summaryMaxTokens=0)
    assert "summaryMaxTokens must be greater than 0" in str(exc_info.value)


def test_compression_config_max_passes_minimum():
    """Test that maxCompressionPasses must be at least 1."""
    with pytest.raises(ValidationError) as exc_info:
        ContextCompressionConfig(maxCompressionPasses=0)
    assert "maxCompressionPasses must be at least 1" in str(exc_info.value)


def test_compression_config_valid():
    """Test that valid configurations are accepted."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=15000,
        targetContextTokens=10000,
        preserveRecentMessages=5,
        summaryMaxTokens=500,
        summaryModel="glm-4-flash",
        maxCompressionPasses=2,
        verbose=True,
    )
    assert config.maxContextTokens == 15000
    assert config.targetContextTokens == 10000
    assert config.preserveRecentMessages == 5
    assert config.summaryModel == "glm-4-flash"
