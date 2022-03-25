"""
Common utility functions
"""
import datetime
from os.path import dirname, join
import re

import jsonref
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from settings import BLOCK_CHAIN

def snake_case(string_to_convert):
    """ Returns snake_case representation of CamelCase string """
    return ''.join(['_'+i.lower() if i.isupper()
                    else i for i in string_to_convert]).lstrip('_')


def dash_snake_case(string_to_convert):
    """ Returns dashed snake_case representation of CamelCase string """
    return ''.join(['-'+i.lower() if i.isupper()
                    else i for i in string_to_convert]).lstrip('-')


def rev_dash_snake_case(string_to_convert):
    """ Returns CamelCase version of dash-snake-case """
    return ''.join(i.capitalize() for i in string_to_convert.split('-'))


def alphabetic_string(string_to_convert):
    """
    Returns alphabetic string removing all special characters and numbers
    """
    return ''.join(i for i in string_to_convert if i.isalpha())


def truncate_string(string_to_truncate, number_of_characters):
    """ Returns string truncated to 10 chars if necessary """
    return (string_to_truncate[:number_of_characters]) \
        if len(string_to_truncate) > number_of_characters \
        else string_to_truncate

def lowercase_with_hyphen_string(string_to_convert):
    """ Returns lowercase string with hyphen """
    converted_string = re.sub(r'[^a-zA-Z_\s-]+', '', string_to_convert)
    converted_string = re.sub(r'[_\s]+', '-', converted_string)
    return converted_string.lower()

def normalize_string(string_to_convert):
    """ Returns normalized string with hyphen """
    converted_string = re.sub(r'[\s().]+', '-', string_to_convert)
    return converted_string

def load_json_schema(filename):
    """ Loads the given json schema file """
    relative_path = join('../schema', filename)
    absolute_path = join(dirname(__file__), relative_path)

    base_path = dirname(absolute_path)
    base_uri = 'file://{}/'.format(base_path)

    with open(absolute_path, encoding="utf8") as schema_file:
        schema_content = schema_file.read().replace('${BLOCK_CHAIN}', BLOCK_CHAIN)
        return jsonref.loads(
            schema_content, base_uri=base_uri, jsonschema=True)


def validate_with_schema(schema_file, data):
    """ Validate data against a specified schema """
    schema = load_json_schema(schema_file)

    try:
        validate(data, schema)
    except ValidationError as v_err:
        return {
            'error': 'Failed schema validation',
            'message': v_err.message,
            'data': data
        }, 422
    except Exception as ex:  # pylint: disable=broad-except
        return {
            'error': 'Unkown schema validation error',
            'message': ex,
            'data': data
        }, 400

    return {
        'message': 'Successfully passed schema validation'
    }, 200


def get_current_timestamp():
    """ Return current timestamp in YYYY-mm-dd HH:MM:SS """
    # return datetime.datetime.now()
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_sort_by_priceUnit(key):
    return key['price']
