import logging
from abc import ABC, abstractmethod
import toml

from src.internal.exception import ApplicationError

class ConfigParser(ABC):
    @abstractmethod
    def parse(self) -> dict:
        pass

class TomlConfigParser(ConfigParser):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def parse(self, path) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                config: dict = toml.load(f)
                return config
            self.logger.info(f"Parsed configuration from {path}")
        except FileNotFoundError:
            self.logger.critical(f"Configuration file not found at {path}")
        except PermissionError:
            self.logger.critical(f"Permission error for configuration file at {path}")
        except toml.TomlDecodeError:
            self.logger.critical(f"Invalid TOML configuration file at {path}")
        except Exception as e:
            self.logger.critical(f"Got an unknown error while parsing TOML configuration file: {e}")

class AbstractConfigParserFactory(ABC):
    @abstractmethod
    def create(self, type: str, logger: logging.Logger) -> ConfigParser:
        pass

class FileConfigParserFactory(ABC):
    @staticmethod
    def create(self, type: str, logger: logging.Logger) -> ConfigParser:
        if type == "toml":
            return TomlConfigParser(logger)
        else:
            raise ApplicationError(f"Unknown config parser type: {type}")
