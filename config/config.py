# -*- coding: utf-8 -*-
"""__init__.py: Package providing the class ```Config```.


Author -- Michael Widrich, Markus Hofmarcher
Created on -- 1/1/17 00:00 AM
Contact -- christian.huber@silicon-austria.com

Package providing the class ```Config```.


=======  ==========  =================  ================================
Version  Date        Author             Description
=======  ==========  =================  ================================
v0.1     1/1/17      Markus Hofmarcher
v0.2     4/12/2021   Christian Huber    Generalise the concept.
=======  ==========  =================  ================================
"""

import os
import logging
from pathlib import Path

from .constants import ENV_CONFIG_NAME, PARENT_CONFIG_TAG, IMPORT_TAG, INCLUDE_TAG
from ._utils import import_object, load_objects, extract_named_args, try_to_number, parse_args, \
    get_file_writer, get_file_loader, get_key, evaluate

__all__ = ['Config']
LOG = logging.getLogger('Config')


class Config:
    """Config object from json/json5 or yaml file.

    Filename can be provided via constructor argument, commandline argument
    '--config', environment variable 'CONFIG_FILE' or if exists the default
    path '.configs/config.json' will be used.

    ## Features:

    ### Parent file:
    A config file can specify a parent config from which it inherits. First,
    the parent file will be loaded (recursively) and afterward current entries
    override or are added to the parent config. The parent config is specified
    by a 'parent' tag at the toplevel of the config file.

    ### Include config
    By setting a value to a string starting with 'include::' followed a filename,
    The tool read an additional config file and inserts it's value replacing the
    include-string.

    ### Import config
    With the import tag, one can load Python modules, packages, classes or functions
    by inserting a value string starting with 'import::' followed by the specification
    of the Python element. The import string will be replaced by the loaded element.

    ### Load objects
    This feature allows to load and instantiate a Python object. A object is specified
    by a dictionary containing a 'class' and a 'params' key. The 'class' key stores a
    string containing the qualified classname and 'params' contains a dictionary
    containing all parameter which will be passed to the constructor of the class.
    Parameter can recursively contain other object definitions.
    """

    def __init__(self, filename: str = None):
        """Create config object from json/json5 or yaml file.

        :param filename: optional;
            If passed read config from specified file.
        """

        if filename is None:
            args, override_args = parse_args(expect_file=True)
            cfile = args.config

            if cfile:
                LOG.debug('Load config from file %s, specified in CLI argument.', cfile)
            else:
                cfile = os.getenv(ENV_CONFIG_NAME, None)

            if cfile:
                LOG.debug('Load config from file %s, specified in environment variable.', cfile)
            else:
                cfile = Path('.', 'configs', 'config.json')
                LOG.debug('Load config from file from fallback path.')
        else:
            LOG.debug('Load config from file %s, specified in parameter.', filename)
            args, override_args = parse_args(expect_file=False)
            cfile = filename

        self._load_config_file(Path(cfile), args, override_args)

    def _load_config_file(self, cfile, args=None, override_args=None):
        # Read config and override with args if passed
        if cfile.exists():
            loader = get_file_loader(cfile.suffix)
            with open(cfile) as file:
                nv_pairs = loader(file.read()).items()
                self._initialize_from_nvpairs(nv_pairs, cfile)

            # override if necessary
            if args is not None:
                pass

            if override_args is not None:
                self._override_from_commandline(override_args, cfile=cfile)
        else:
            ex = IOError(f'Configuration file {cfile} does not exist!')
            LOG.exception(ex)
            raise ex

    def _import_value_rec(self, value, cfile):
        if isinstance(value, str) and IMPORT_TAG in value:
            try:
                LOG.debug('Import object: %s', value[len(IMPORT_TAG):])
                value = import_object(value[len(IMPORT_TAG):])
            except ModuleNotFoundError:
                LOG.error('Unable to import "%s"', value, exc_info=True)

        elif isinstance(value, str) and INCLUDE_TAG in value:
            LOG.debug('Include object: %s', value[len(INCLUDE_TAG):])
            base_path = Path(value[len(INCLUDE_TAG):]).relative_to(cfile.parent)
            value = Config(str(base_path)).__dict__

        elif isinstance(value, dict):
            for key, val in value.items():
                value[key] = self._import_value_rec(val, cfile)

        elif isinstance(value, list):
            for i, val in enumerate(value):
                value[i] = self._import_value_rec(val, cfile)

        return value

    def _set_attribute(self, name, value, cfile):
        if value is not None:
            value = self._import_value_rec(value, cfile)
            setattr(self, name, value)
            LOG.debug('CONFIG: %s=%s', name, value)

    def get(self, name, *args, default=None, instance=True, dictionary=None, **kwargs):
        """
        Loads a value from the config. If the value contains a class specification,
        the object will be loaded.

        :param name: Name of the attribute to return
        :param default: Default value if 'name' was not found
        :param instance: If false a class will just be imported but not instantiated
        :param dictionary: Dictionary to searche for 'name'. If not provided the
                            Config toplevel is used
        :param args: Positional arguments to instantiate objects
        :param kwargs: Keyword arguments to instantiate objects
                            (override config file values)
        :return: A configuration value for 'name'
        """
        if dictionary is None:
            dictionary = self.__dict__

        if name not in dictionary:
            return default

        val = dictionary.get(name)
        return load_objects(val, *args, instance=instance, **kwargs)

    def __getitem__(self, item):
        value = self.get(item)
        if value:
            return value

        raise KeyError

    def __getattribute__(self, item):
        if item not in dir(Config):
            value = self.get(item)
            if value:
                return value

            raise AttributeError

        return object.__getattribute__(self, item)

    def _initialize_from_nvpairs(self, nv_pairs=None, cfile=None):
        if nv_pairs:
            for name, value in nv_pairs:
                if PARENT_CONFIG_TAG == name and value is not None:
                    base_path = Path(value).relative_to(cfile.parent)
                    LOG.debug('Load parent config: %s', base_path)
                    self._load_config_file(base_path)
                else:
                    self._set_attribute(name, value, cfile)

    def _override_from_commandline(self, override_args=None, cfile=None):
        if override_args is None:
            return

        override = extract_named_args(override_args)
        for key, val in override.items():
            name = key[2:] if '--' in key else key  # remove leading --
            value = val if val is None or val.startswith('"') or val.startswith("'") else try_to_number(val)
            LOG.debug('Override key "%s" with value "%s"', name, value)

            value = evaluate(value)

            current = self.__dict__
            names = name.split('.')

            if len(names) == 1:
                self._set_attribute(names[0], value, cfile)
                continue

            for i, cur_key in enumerate(names):
                last = i == len(names)-1
                idx = get_key(current, cur_key)

                if idx is None and not last:
                    new_current = {}
                    idx = cur_key
                    if isinstance(try_to_number(names[i + 1]), int):
                        new_current = []

                    if i == 0:
                        self._set_attribute(idx, new_current, cfile)
                    elif isinstance(current, dict):
                        current[idx] = new_current
                    else:
                        assert isinstance(current, list)
                        # pylint: disable=no-member
                        current.append(new_current)

                    current = new_current
                elif not last:
                    current = current[idx]
                else:
                    idx = try_to_number(cur_key)
                    current[idx] = value

    def save_to(self, filename):
        """Saved the current configuration to a file.

        :param file: filename to save the configuration to
        """""
        LOG.debug('Safe config to %s', filename)
        writer = get_file_writer(Path(filename).suffix)
        with open(filename, 'w') as file:
            writer(self.__dict__, file, indent=2, sort_keys=True)
