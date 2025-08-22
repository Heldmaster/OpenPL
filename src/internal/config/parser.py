import logging
from abc import ABC, abstractmethod
import toml

from src.internal.exception import ApplicationError


class ConfigParser(ABC):
    @abstractmethod
    def parse(self, path) -> tuple[dict, dict]:
        pass


class TomlConfigParser(ConfigParser):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def parse(self, path) -> tuple[dict, dict]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_parsed: dict = toml.load(f)
                config = self._ParseConfig(raw_parsed)

                tags: dict = None
                if raw_parsed["platform"]["type"] == "vision_fiducial":
                    tags = self._ParseTagsSeq(raw_parsed)

                print(tags)
                return config, tags
            self.logger.info(f"Parsed configuration from {path}")
        except FileNotFoundError:
            self.logger.critical(f"Configuration file not found at {path}")
        except PermissionError:
            self.logger.critical(f"Permission error for configuration file at {path}")
        except toml.TomlDecodeError:
            self.logger.critical(f"Invalid TOML configuration file at {path}")
        except Exception as e:
            self.logger.critical(
                f"Got an unknown error while parsing TOML configuration file: {e}"
            )

    def _ParseConfig(self, raw_parsed: dict) -> dict:
        config_copy: dict = raw_parsed.copy()

        if "vision_fiducial" in config_copy:
            del config_copy["vision_fiducial"]

        return config_copy

    def _ParseTagsSeq(self, raw_parsed: dict) -> dict:
        tags_dict: dict = {}
        vision_fiducial: dict = raw_parsed.get("vision_fiducial", {})
        tags_list: list = vision_fiducial.get("tags", [])

        for tag in tags_list:
            tag_id = tag.get("id")
            tag_size = tag.get("size")

            if tag_id is not None and tag_size is not None:
                tags_dict[tag_id] = tag_size

        return tags_dict


class AbstractConfigParserFactory(ABC):
    @abstractmethod
    def create(self, type: str, logger: logging.Logger) -> ConfigParser:
        pass


class FileConfigParserFactory(ABC):
    @classmethod
    def create(self, type: str, logger: logging.Logger) -> ConfigParser:
        if type == "toml":
            return TomlConfigParser(logger)
        else:
            raise ApplicationError(f"Unknown config parser type: {type}")
