"""Configuration settings loaded from config.yaml and environment variables."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from functools import lru_cache


class Settings:
    """Application settings loaded from config.yaml."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings from config file.

        Args:
            config_path: Path to config.yaml file. If None, looks in project root.
        """
        if config_path is None:
            # Look for config.yaml in project root
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            config_path = project_root / "config.yaml"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Substitute environment variables
        self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, config: Any) -> None:
        """
        Recursively substitute ${VAR_NAME} with environment variables.

        Args:
            config: Configuration dictionary or value
        """
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    config[key] = os.getenv(env_var, '')
                elif isinstance(value, (dict, list)):
                    self._substitute_env_vars(value)
        elif isinstance(config, list):
            for i, item in enumerate(config):
                if isinstance(item, str) and item.startswith('${') and item.endswith('}'):
                    env_var = item[2:-1]
                    config[i] = os.getenv(env_var, '')
                elif isinstance(item, (dict, list)):
                    self._substitute_env_vars(item)

    # App settings
    @property
    def app_name(self) -> str:
        return self._config.get('app', {}).get('name', 'EngageIQ')

    @property
    def app_version(self) -> str:
        return self._config.get('app', {}).get('version', '1.0.0')

    @property
    def environment(self) -> str:
        return self._config.get('app', {}).get('environment', 'development')

    @property
    def debug(self) -> bool:
        return self._config.get('app', {}).get('debug', False)

    # API settings
    @property
    def api_host(self) -> str:
        return self._config.get('api', {}).get('host', '0.0.0.0')

    @property
    def api_port(self) -> int:
        return self._config.get('api', {}).get('port', 8000)

    @property
    def cors_origins(self) -> list:
        return self._config.get('api', {}).get('cors_origins', [])

    # Data settings
    @property
    def data_sources(self) -> Dict[str, str]:
        return self._config.get('data', {}).get('sources', {})

    @property
    def data_connector(self) -> str:
        return self._config.get('data', {}).get('connector', 'csv')

    # Connector settings
    @property
    def connectors(self) -> Dict[str, Any]:
        return self._config.get('connectors', {})

    def get_connector_config(self, connector_type: str) -> Dict[str, Any]:
        """Get configuration for a specific connector type."""
        return self.connectors.get(connector_type, {})

    # LLM settings
    @property
    def llm_default_provider(self) -> str:
        return self._config.get('llm', {}).get('default_provider', 'claude')

    @property
    def llm_providers(self) -> Dict[str, Any]:
        return self._config.get('llm', {}).get('providers', {})

    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific LLM provider."""
        return self.llm_providers.get(provider, {})

    # Agent settings
    @property
    def agents(self) -> Dict[str, Any]:
        return self._config.get('agents', {})

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.agents.get(agent_name, {})

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Dot-separated key (e.g., 'app.name')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value


@lru_cache()
def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get cached settings instance.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Settings instance
    """
    return Settings(config_path)