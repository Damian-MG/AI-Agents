"""
This files loads the required secrets from the .env file into de mcp_config.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


def resolve_env_vars(config: dict) -> dict:
    for server_name, server_config in config["mcpServers"].items():
        for feature in server_config.keys():

            if feature == "env":
                for key, value in server_config[feature].items():
                    if isinstance(value, str) and value.startswith("${"):
                        env_var_name = value[2:-1]
                        env_var_value = os.environ.get(env_var_name, None)
                        if env_var_value is None:
                            raise ValueError(
                                f"Environment variable {env_var_name} not set")
                        config["mcpServers"][server_name][feature][
                            key] = env_var_value

            if feature == "args":
                for i, arg in server_config[feature]:
                    if isinstance(arg, str) and arg.startswith("${"):
                        env_var_name = arg[2:-1]
                        env_var_value = os.environ.get(env_var_name, None)
                        if env_var_value is None:
                            raise ValueError(
                                f"Environment variable {env_var_name} not set")
                        config["mcpServers"][server_name][feature][
                            i] = env_var_value
    return config


config_file = Path(__file__).parent / "mcp_config.json"

if not config_file.exists():
    raise FileNotFoundError(
        f"mcp_config.json file {config_file} does not exist")

with open(config_file, "r", encoding="utf-8") as f:
    conf = json.load(f)

mcp_config = resolve_env_vars(conf)
