"""_utils.py: Test utils.


Author -- Christian Huber
Created on -- 4/13/21 10:26 AM
Contact -- christian.huber@silicon-austria.com

Utility functions for unit tests.


=======  ==========  =================  ================================
Version  Date        Author             Description
=======  ==========  =================  ================================

"""

import io
import json
from unittest.mock import MagicMock


__all__ = ['Dummy', 'get_config_mock']


class Dummy:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class MMock:
    def __init__(self, fnc):
        self.fnc = fnc

    def save_arg_return_data(self, *args, **kwargs):
        file_spec = list(set(dir(io.TextIOWrapper)).union(set(dir(io.BytesIO))))

        mm = MagicMock(spec=file_spec)
        sio = io.StringIO(json.dumps(self.fnc(args[0], default={})))
        mm.__enter__.return_value = sio
        return mm


def get_config_mock(sample_fn):
    m = MagicMock()
    mm = MMock(sample_fn)

    m.side_effect = mm.save_arg_return_data
    return m
