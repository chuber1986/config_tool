"""_samples.py: Sample configurations


Author -- Christian Huber
Created on -- 4/13/21 10:27 AM
Contact -- christian.huber@silicon-austria.com

Samples configurations for unit tests


=======  ==========  =================  ================================
Version  Date        Author             Description
=======  ==========  =================  ================================

"""

import copy
from config.constants import IMPORT_TAG, INCLUDE_TAG, CLASS_TAG,\
    PARENT_CONFIG_TAG, OBJECT_PARM_TAG

from tests._utils import Dummy


_SAMPLE_01 = {
    'a': 123,
    'b': [1, 2, 3],
    'c': {'ca': 1, 'cb': 2, 'cc': 3},
    'd': [{'ca': 1, 'cb': 2, 'cc': 3},
          {'ca': 1, 'cb': 2, 'cc': 3}],
    'e': {'ca': [1, 2, 3],
          'cb': [1, 2, 3]}
}

_TARGET_01 = copy.deepcopy(_SAMPLE_01)

_SAMPLE_02 = {
    PARENT_CONFIG_TAG: 'SAMPLE_01',
    'a': 321,
    'e': {'ca': [1, 2, 3],
          'cb': [3, 2, 1]}
}

_TARGET_02 = copy.deepcopy(_SAMPLE_01)
_TARGET_02.update(_SAMPLE_02)
_TARGET_02.pop(PARENT_CONFIG_TAG)

_SAMPLE_03 = {
    'c': {'ca': 1,
          'cb': f'{IMPORT_TAG}tests._utils.Dummy',
          'cc': 3}
}

_TARGET_03 = copy.deepcopy(_SAMPLE_03)
_TARGET_03['c']['cb'] = Dummy

_sample_04_inc01 = {'cca': 1, 'ccb': 2}
_SAMPLE_04 = {
    'c': {'ca': f'{INCLUDE_TAG}sample_04_inc01'}
}

_TARGET_04 = {
    'c': {'ca': {'cca': 1, 'ccb': 2}}
}

_SAMPLE_05 = {
    'c': {'ca': 1,
          'cb': [{
              CLASS_TAG: 'tests._utils.Dummy',
              OBJECT_PARM_TAG: {'a': 1, 'b': 2, 'c': 3}
          }, {
              CLASS_TAG: 'tests._utils.Dummy',
              OBJECT_PARM_TAG: [1, 2, 3]
          }]}
}

_TARGET_05 = {
    'c': {'ca': 1,
          'cb': [Dummy(a=1, b=2, c=3),
                 Dummy(1, 2, 3)]}
}

SAMPLE_COLLECTION = {
    'SAMPLE_01':       (_SAMPLE_01, _TARGET_01),
    'SAMPLE_02':       (_SAMPLE_02, _TARGET_02),
    'SAMPLE_03':       (_SAMPLE_03, _TARGET_03),
    'SAMPLE_04':       (_SAMPLE_04, _TARGET_04),
    'sample_04_inc01': (_sample_04_inc01, ),
    'SAMPLE_05':       (_SAMPLE_05, _TARGET_05),
}


def get_sample(sml, default=dict()):
    sample = str(sml)
    if sample in SAMPLE_COLLECTION:
        s = SAMPLE_COLLECTION[sample][0]
    else:
        s = default

    return s


def get_target(trg, default=None):
    if trg in SAMPLE_COLLECTION:
        s = SAMPLE_COLLECTION[trg][1]
    else:
        s = default

    return s
