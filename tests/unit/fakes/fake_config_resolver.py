#!/usr/bin/python3

# fake_config_resolver.py
# Date:  20/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

class FakeConfigResolver(object):

    @property
    def PWDB_XXX(self):
        return EnvConfigResolver.config_resolve(default_value="baubau")
