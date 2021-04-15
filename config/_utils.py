"""_utils.py: Collection of generic functions used by the config tool.


Author -- Christian Huber
Created on -- 4/12/21 10:59 AM
Contact -- christian.huber@silicon-austria.com

Collection of generic functions used by the config tool.


=======  ==========  =================  ================================
Version  Date        Author             Description
=======  ==========  =================  ================================

"""

import logging
import importlib
import argparse

from .constants import CLASS_TAG, OBJECT_PARM_TAG, CONFIG_ARG_TAG


__all__ = ['parse_args', 'extract_named_args', 'try_to_number', 'get_file_loader', 'get_file_writer',
           'import_object', 'load_objects', 'get_key', 'evaluate']


def parse_args(expect_file=True):
    """
    Configure and run ArgumentParser for ConfigTool.

    :param expect_file: expect config file definitions

    :return: config file argument and override arguments
    """
    parser = argparse.ArgumentParser()
    if expect_file:
        parser.add_argument(CONFIG_ARG_TAG, type=str, default=None, help="JSON file with the model params")
    args, override_args = parser.parse_known_args()
    if len(override_args) == 0:
        override_args = None
    return args, override_args


def extract_named_args(arglist):
    """Extract named arguments from list of arguments"""
    result = {}
    for i, arg in enumerate(arglist):
        if arg.startswith("--"):
            if i + 1 < len(arglist) and not arglist[i + 1].startswith("--"):
                result[arg] = arglist[i + 1]
            else:
                result[arg] = None
    return result


def extract_unnamed_args(arglist):
    """Extract unnamed arguments from list of arguments"""
    result = []
    for i in range(1, len(arglist)):
        arg = arglist[i]
        prev = arglist[i - 1]
        if not arg.startswith("--") and not prev.startswith("--"):
            result.append(arg)
    return result


def try_to_number(value):
    """Tries to convert a string into a number otherwise returns the string."""
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass
    return value


def get_file_loader(ext):
    """Returns a load function for a given file extension."""
    # pylint: disable=import-outside-toplevel
    ext = ext.lower()[1:]
    try:
        if ext == '.json':
            try:
                import json
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return json.loads

        if ext == '.json5':
            try:
                import json5
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return json5.loads

        if ext == '.xml':
            try:
                import xmltodict
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return xmltodict.parse

        if ext in ('.yml', '.yaml'):
            try:
                import yaml
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return yaml.load

        ex = Exception(f"Unknown configuration filetype {ext}!")
        logging.exception(ex)
        raise ex
    except ImportError as ex:
        logging.exception(ex)


def get_file_writer(ext):
    """Returns a write function for a given file extension."""
    # pylint: disable=import-outside-toplevel
    ext = ext.lower()[1:]
    try:
        if ext == '.json':
            try:
                import json
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return json.dump

        if ext == '.json5':
            try:
                import json5
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return json5.dump

        if ext in ('.yml', '.yaml'):
            try:
                import yaml
            except ImportError:
                logging.error('Error importing: json', exc_info=True)
            return yaml.load

        ex = Exception(f"Unknown configuration filetype {ext}!")
        logging.exception(ex)
        raise ex
    except ImportError as ex:
        logging.exception(ex)


def import_object(objname):
    """Import a Pyhton object specified a string."""
    module_str = objname.split('.', maxsplit=1)
    objmodule = importlib.import_module(module_str[0])
    return _get_rec_attr(objmodule, module_str[-1])


def _get_rec_attr(obj, attrstr):
    """Get attributes and do so recursively if needed"""
    if attrstr is None:
        return None
    if "." in attrstr:
        attrs = attrstr.split('.', maxsplit=1)
        if hasattr(obj, attrs[0]):
            obj = _get_rec_attr(getattr(obj, attrs[0]), attrs[1])
        else:
            try:
                obj = _get_rec_attr(importlib.import_module(obj.__name__ + "." + attrs[0]), attrs[1])
            except ImportError:
                logging.error('Error importing: json', exc_info=True)

    else:
        if hasattr(obj, attrstr):
            obj = getattr(obj, attrstr)
    return obj


def load_objects(val, *args, instance=True, **kwargs):
    """
    Iterates over a Python structure and loads object from string representations.
    A string representation is a dictionary containing a 'class' tag
    storing a class representing string.
    A optional second key, 'param', holds a dictionary with keyword arguments
    to initialize an object.

    :param val: Python structure to iterate through
    :param instance: Returns an initialized object if 'True', the class if 'False'
    :param args: Positional argument for the constructor
    :param kwargs: Additional (override) arguments for the constructor
    :return: 'val' with loaded objects
    """
    if isinstance(val, list):
        return [load_objects(o, *args, instance=instance, **kwargs) for o in val]

    if isinstance(val, dict) and CLASS_TAG not in val:
        return {k: load_objects(v, *args, instance=instance, **kwargs) for k, v in val.items()}

    if isinstance(val, dict):
        return _load_configured_object(val, *args, instance=instance, **kwargs)

    return val


def _load_configured_object(obj, *args, instance=True, **kwargs):
    """Loads an object from it's string representation."""
    if isinstance(obj, dict) and CLASS_TAG in obj:
        cls = import_object(obj[CLASS_TAG])

        if not instance:
            return cls

        params = {}
        if OBJECT_PARM_TAG in obj:
            params = load_objects(obj[OBJECT_PARM_TAG])

        assert isinstance(params, (dict, list))
        if isinstance(params, dict):
            kwargs.update(params)
        else:
            args += tuple(params)

        return cls(*args, **kwargs)

    return obj


def get_key(colletion, key):
    """Returns a valid key for a collection or None"""
    if isinstance(colletion, dict) and key in colletion:
        return key

    ikey = try_to_number(key)
    if isinstance(colletion, list) and ikey in range(len(colletion)):
        return ikey

    return None


def evaluate(value):
    """Evaluate a string as Python expression"""
    if not isinstance(value, str):
        return value

    try:
        # pylint: disable=eval-used
        value = eval(value)
    except (ValueError, SyntaxError):
        pass

    return value
