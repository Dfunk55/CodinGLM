"""Configuration management for CodinGLM."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv


def _load_env_files() -> None:
    """Load environment variables from common locations.

    We support `.env` (project/home), `env.env`, and an optional
    `CODINGLM_ENV_FILE` override (with backward compatibility for
    `GLM_CODER_ENV_FILE`) so the clone mirrors Claude Code's flexible
    configuration.
    """
    loaded_paths: set[str] = set()

    def _load_candidate(candidate: Path | str | None) -> None:
        if not candidate:
            return

        path = Path(candidate).expanduser()
        if not path.exists():
            return

        resolved = str(path.resolve())
        if resolved in loaded_paths:
            return

        load_dotenv(dotenv_path=resolved, override=False)
        loaded_paths.add(resolved)

    # Default .env discovery (dotenv walks parents)
    load_dotenv(override=False)

    project_root = Path(__file__).resolve().parents[1]
    env_file_override = os.getenv("CODINGLM_ENV_FILE") or os.getenv("GLM_CODER_ENV_FILE")

    candidates: List[Path | str | None] = [
        env_file_override,
        Path.cwd() / "env.env",
        Path.cwd() / ".env.local",
        project_root / ".env",
        project_root / "env.env",
        Path.home() / ".env",
        Path.home() / "env.env",
        Path.home() / "Dev-Projects/env.env",
    ]

    for candidate in candidates:
        _load_candidate(candidate)


_load_env_files()


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)


class ToolsConfig(BaseModel):
    """Configuration for tool behavior."""
    autoApprove: List[str] = Field(default_factory=list)
    maxToolIterations: Optional[int] = None

    @field_validator("maxToolIterations")
    @classmethod
    def validate_max_tool_iterations(cls, v: Optional[int]) -> Optional[int]:
        """Ensure maxToolIterations is positive when provided."""
        if v is not None and v < 1:
            raise ValueError("maxToolIterations must be at least 1")
        return v


class UIConfig(BaseModel):
    """Configuration for UI/UX."""
    theme: str = "monokai"
    showTimestamps: bool = False
    compactMode: bool = False


class ContextCompressionConfig(BaseModel):
    """Settings for automatic context compression.

    Default values maximize GLM-4.6's 200K context window for subscription users.
    Optimized for longest possible sessions with minimal compression.
    """
    enabled: bool = True
    maxContextTokens: int = 185000  # 92.5% of GLM-4.6's 200K context window
    targetContextTokens: int = 165000  # 82.5% of GLM-4.6's 200K context window
    preserveRecentMessages: int = 15  # Maximum context retention
    summaryMaxTokens: int = 2000  # Detailed summaries for better continuity
    summaryModel: Optional[str] = None
    maxCompressionPasses: int = 3
    verbose: bool = False

    @field_validator("maxContextTokens")
    @classmethod
    def validate_max_context_tokens(cls, v: int) -> int:
        """Ensure maxContextTokens is positive."""
        if v <= 0:
            raise ValueError("maxContextTokens must be greater than 0")
        return v

    @field_validator("targetContextTokens")
    @classmethod
    def validate_target_context_tokens(cls, v: int, info) -> int:
        """Ensure targetContextTokens is positive and less than maxContextTokens."""
        if v <= 0:
            raise ValueError("targetContextTokens must be greater than 0")
        # Note: We can't access maxContextTokens here during initialization
        # This will be checked in model_validator
        return v

    @field_validator("preserveRecentMessages")
    @classmethod
    def validate_preserve_recent_messages(cls, v: int) -> int:
        """Ensure preserveRecentMessages is at least 1 to avoid confusing behavior."""
        if v < 1:
            raise ValueError(
                "preserveRecentMessages must be at least 1 to preserve recent context. "
                "Setting to 0 would compress all messages including the most recent."
            )
        return v

    @field_validator("summaryMaxTokens")
    @classmethod
    def validate_summary_max_tokens(cls, v: int) -> int:
        """Ensure summaryMaxTokens is positive."""
        if v <= 0:
            raise ValueError("summaryMaxTokens must be greater than 0")
        return v

    @field_validator("maxCompressionPasses")
    @classmethod
    def validate_max_compression_passes(cls, v: int) -> int:
        """Ensure maxCompressionPasses is positive."""
        if v < 1:
            raise ValueError("maxCompressionPasses must be at least 1")
        return v

    def model_post_init(self, __context) -> None:
        """Validate relationships between fields after initialization."""
        if self.targetContextTokens >= self.maxContextTokens:
            raise ValueError(
                f"targetContextTokens ({self.targetContextTokens}) must be less than "
                f"maxContextTokens ({self.maxContextTokens})"
            )


class ContextConfig(BaseModel):
    """Top-level conversation context settings."""
    compression: ContextCompressionConfig = Field(default_factory=ContextCompressionConfig)


class Config(BaseModel):
    """Main configuration for CodinGLM."""
    apiKey: Optional[str] = None
    model: str = "glm-4.6"
    temperature: float = 0.7
    maxTokens: int = 8192
    apiBase: str = "https://api.z.ai/api/anthropic"
    apiTimeoutMs: int = 600000
    mcpServers: Dict[str, MCPServerConfig] = Field(default_factory=dict)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from file or defaults.

        Search order:
        1. Provided config_path
        2. .codinglm.json in current directory
        3. .codinglm.json in home directory
        4. Default configuration
        """
        config_data: Dict[str, Any] = {}

        # Search for config file
        if config_path is None:
            search_paths = [
                Path.cwd() / ".codinglm.json",
                Path.home() / ".codinglm.json",
            ]
            for path in search_paths:
                if path.exists():
                    config_path = path
                    break

        # Load config file if found
        if config_path and config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)

            # Replace environment variable placeholders
            config_data = cls._resolve_env_vars(config_data)

        # Override with environment variables
        api_key_env_vars = (
            "Z_AI_API_KEY",
            "ZAI_API_KEY",
            "ANTHROPIC_AUTH_TOKEN",
        )
        for env_var in api_key_env_vars:
            api_key = os.getenv(env_var)
            if api_key:
                config_data["apiKey"] = api_key
                break

        model_env_vars = (
            "CODINGLM_MODEL",
            "GLM_CODER_MODEL",
            "ANTHROPIC_DEFAULT_OPUS_MODEL",
            "ANTHROPIC_DEFAULT_SONNET_MODEL",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        )
        for env_var in model_env_vars:
            model = os.getenv(env_var)
            if model:
                config_data["model"] = model
                break

        base_url_env_vars = (
            "CODINGLM_BASE_URL",
            "GLM_CODER_BASE_URL",
            "ANTHROPIC_BASE_URL",
            "Z_AI_BASE_URL",
        )
        for env_var in base_url_env_vars:
            base = os.getenv(env_var)
            if base:
                config_data["apiBase"] = base
                break

        timeout_env_vars = (
            "CODINGLM_TIMEOUT_MS",
            "GLM_CODER_TIMEOUT_MS",
            "API_TIMEOUT_MS",
            "ANTHROPIC_TIMEOUT_MS",
        )
        for env_var in timeout_env_vars:
            timeout_value = os.getenv(env_var)
            if timeout_value:
                parsed = Config._try_parse_int(timeout_value)
                if parsed is not None:
                    config_data["apiTimeoutMs"] = parsed
                    break

        return cls(**config_data)

    @staticmethod
    def _resolve_env_vars(data: Any) -> Any:
        """Recursively resolve ${VAR} patterns in config."""
        if isinstance(data, dict):
            return {k: Config._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [Config._resolve_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            return os.getenv(var_name, data)
        return data

    def get_api_key(self) -> str:
        """Get API key, raising error if not set."""
        if not self.apiKey:
            raise ValueError(
                "Z.ai API key not configured. Set Z_AI_API_KEY (or legacy "
                "ZAI_API_KEY/ANTHROPIC_AUTH_TOKEN) environment variable, or add "
                "'apiKey' to .codinglm.json"
            )
        return self.apiKey

    @staticmethod
    def _try_parse_int(value: str) -> Optional[int]:
        """Attempt to parse an integer value."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
