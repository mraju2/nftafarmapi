""" Collection of Validation functions """
import re


def is_all_caps_alpha_underscore(string):
    """
    Checks if string is:
        - all CAPS
        - A-Z and underscores allowed
        - No spaces or special characters except underscore
    """
    schema = re.compile('^[A-Z_]+$')
    return schema.match(string)
