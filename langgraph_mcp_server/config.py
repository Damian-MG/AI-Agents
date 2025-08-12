"""
This files loads the required secrets from the .env file into de mcp_config.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


def resolve_env_vars(config: dict) -> dict:
    