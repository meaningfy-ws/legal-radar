#!/usr/bin/python3

# __init__.py
# Date:  18/11/2021
# Author: Stratulat Stefan
# Email: stefan.stratulat1997@gmail.com 

"""

"""
import logging
import warnings

import dotenv

from mfy_data_core.adapters.config_resolver import VaultAndEnvConfigResolver, EnvConfigResolver
from mfy_data_core.adapters.vault_secrets_store import VaultSecretsStore

logger = logging.getLogger(__name__)

dotenv.load_dotenv(verbose=True, override=True)

SECRET_PATHS = ['air-flow', 'elastic-search', 'jupyter-notebook', 'min-io', 'ml-flow', 'sem-covid',
                'sem-covid-infra']
SECRET_MOUNT = 'mfy'

# use this settings when lega-radar infra is ready
#SECRET_PATHS = ['elastic-search', 'notebook', 'minio', 'legal-radar']
#SECRET_MOUNT = 'lr'

VaultSecretsStore.default_secret_mount = SECRET_MOUNT
VaultSecretsStore.default_secret_paths = SECRET_PATHS


class MinIOConfig:
    # MinIO Service property
    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MINIO_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

class EuFinRegConfig:
    # EU_FINREG property

    @property
    def EU_FINREG_CELLAR_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_FINREG_CELLAR_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()



class LegalInitiativesConfig:
    # LEGAL_INITIATIVES property

    @property
    def LEGAL_INITIATIVES_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def LEGAL_INITIATIVES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class TreatiesConfig:
    # TREATIES property
    @property
    def TREATIES_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_SPARQL_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class TikaConfig:
    # TIKA property
    @property
    def APACHE_TIKA_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class SplashConfig:
    # SPLASH property
    @property
    def SPLASH_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class ElasticSearchConfig:
    # ELASTICSEARCH property
    @property
    def ELASTICSEARCH_PROTOCOL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_HOST_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_PORT(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_USERNAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_PASSWORD(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class VaultConfig:
    # Vault property

    @property
    def VAULT_ADDR(self) -> str:
        return EnvConfigResolver.config_resolve()

    @property
    def VAULT_TOKEN(self) -> str:
        return EnvConfigResolver.config_resolve()


class LegalRadarConfig(VaultConfig,
                     ElasticSearchConfig,
                     TikaConfig,
                     SplashConfig,
                     TreatiesConfig,
                     LegalInitiativesConfig,
                     EuFinRegConfig,
                     MinIOConfig
                     ):
    ...


config = LegalRadarConfig()

