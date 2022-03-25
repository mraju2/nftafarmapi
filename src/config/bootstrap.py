""" Bootstrap Configuration """
from config.config import load_configs
from config.profile import load_profiles

def config_bootstrap():
    """ Bootstrap Configuration """
    load_configs()
    load_profiles()
    
