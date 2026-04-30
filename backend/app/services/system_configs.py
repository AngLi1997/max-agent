from app.models.system_config import SystemConfig


def update_config_value(
    config: SystemConfig,
    *,
    name: str,
    key: str,
    value: str,
    description: str,
) -> None:
    config.name = name
    config.key = key
    config.value = value
    config.description = description
