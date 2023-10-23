"""
    This module aims to store the configuration of the application.
"""

import logging
import dotenv

from legal_radar.adapters.config_resolver import EnvConfigResolver, env_property

logger = logging.getLogger(__name__)

dotenv.load_dotenv(verbose=True, override=True)


class MilvusConfig:

    @env_property()
    def MILVUS_HOST(self, config_value: str) -> str:
        return config_value

    @env_property()
    def MILVUS_PORT(self, config_value: str) -> str:
        return config_value


class LegalRadarConfig(MilvusConfig):
    """
        This class aims to store the configuration of the application.
    """


config = LegalRadarConfig()
