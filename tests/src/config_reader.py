from configparser import ConfigParser
from pathlib import Path

ROOT = Path(__file__).parent.parent


def build_config_parser():
    config_file_path = Path(ROOT / "configurations.config").resolve()
    parser = ConfigParser()
    parser.read(config_file_path)
    return parser


def get_configuration_value(section, key):
    parser = build_config_parser()
    return parser.get(section, key)


def get_path_from_config(path_key):
    path = Path(str(ROOT) + get_configuration_value("PATHS", path_key))
    return path
