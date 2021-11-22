#!/usr/bin/python3

# data.py
# Date:  19/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    A registry of the frequently used datasets and language models
"""

from legal_radar import config

"""
   These constants represent the name of the index in ElasticSearch,
     which consist of the original index name and the label for enriched datasets.
"""

class Dataset(object):
    """
        Registry of dataset sources
    """
    #PWDB = IndexTabularDataSource(config.PWDB_ELASTIC_SEARCH_INDEX_NAME, StoreRegistry.es_index_store())

