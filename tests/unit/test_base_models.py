"""_utils.py: Tests for the ```Config``` class.


Author -- Christian Huber
Created on -- 4/13/21 10:26 AM
Contact -- christian.huber@silicon-austria.com

Tests for the ```Config``` class.


=======  ==========  =================  ================================
Version  Date        Author             Description
=======  ==========  =================  ================================

"""

import os
import sys
import json
from pathlib import Path

from unittest import TestCase
from unittest.mock import patch

from config import Config
from config.constants import ENV_CONFIG_NAME, CONFIG_ARG_TAG
from tests._utils import get_config_mock
from tests._samples import get_sample, get_target


class TestConfig(TestCase):

    @classmethod
    def setUpClass(cls):
        TestConfig.argv = list(sys.argv)
        sys.argv = sys.argv[:1]

    @classmethod
    def tearDownClass(cls):
        sys.argv = TestConfig.argv

    def setUp(self):
        self.patch_exists = patch('config.config.Path.exists', return_value=True)
        self.patch_exists.start()
        self.addCleanup(self.patch_exists.stop)

        self.patch_file_loader = patch('config.config.get_file_loader', return_value=json.loads)
        self.patch_file_loader.start()
        self.addCleanup(self.patch_file_loader.stop)

        self.mock_open = get_config_mock(get_sample)
        self.patch_open = patch('builtins.open', self.mock_open, create=True)
        self.patch_open.start()
        self.addCleanup(self.patch_open.stop)

    def tearDown(self):
        super(TestConfig, self).tearDown()

    def test_init_default_file(self):
        Config()

        self.mock_open.assert_called_once()
        self.mock_open.assert_called_with(Path('.', 'configs', 'config.json'))

    def test_init_env(self):
        os.environ[ENV_CONFIG_NAME] = 'config_1.json'
        Config()
        os.environ.pop(ENV_CONFIG_NAME)

        self.mock_open.assert_called_once()
        self.mock_open.assert_called_with(Path('config_1.json'))

    def test_init_cli_arg(self):
        args = [CONFIG_ARG_TAG, 'config_3.json']
        sys.argv += args

        try:
            Config()
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.mock_open.assert_called_once()
        self.mock_open.assert_called_with(Path('config_3.json'))

    def test_init_filename(self):
        Config('config_2.json')

        self.mock_open.assert_called_once()
        self.mock_open.assert_called_with(Path('config_2.json'))

    def test_init_filename_not_exists(self):
        self.patch_exists.stop()
        self.assertRaises(IOError, Config, 'not_exist.json')
        self.patch_exists.start()

    def test_simple_config(self):
        c = Config('SAMPLE_01')
        self.assertDictEqual(get_target('SAMPLE_01'), c.__dict__)

    def test_parent_config(self):
        c = Config('SAMPLE_02')
        self.assertDictEqual(get_target('SAMPLE_02'), c.__dict__)

    def test_import_class(self):
        c = Config('SAMPLE_03')
        self.assertDictEqual(get_target('SAMPLE_03'), c.__dict__)

    def test_include_config(self):
        c = Config('SAMPLE_04')
        self.assertDictEqual(get_target('SAMPLE_04'), c.__dict__)

    def test_load_object(self):
        c = Config('SAMPLE_05')

        to1 = get_target('SAMPLE_05')['c']['cb'][0]
        to2 = get_target('SAMPLE_05')['c']['cb'][1]

        co1 = c.c['cb'][0]
        co2 = c.c['cb'][1]

        self.assertTupleEqual(to1.args, co1.args)
        self.assertDictEqual(to1.kwargs, co1.kwargs)
        self.assertTupleEqual(to2.args, co2.args)
        self.assertDictEqual(to2.kwargs, co2.kwargs)

        co1 = c['c']['cb'][0]
        co2 = c['c']['cb'][1]

        self.assertTupleEqual(to1.args, co1.args)
        self.assertDictEqual(to1.kwargs, co1.kwargs)
        self.assertTupleEqual(to2.args, co2.args)
        self.assertDictEqual(to2.kwargs, co2.kwargs)

        co1 = c.get('c')['cb'][0]
        co2 = c.get('c')['cb'][1]
        self.assertTupleEqual(to1.args, co1.args)
        self.assertDictEqual(to1.kwargs, co1.kwargs)
        self.assertTupleEqual(to2.args, co2.args)
        self.assertDictEqual(to2.kwargs, co2.kwargs)

    def test_init_cli_override1(self):
        args = ['--b', '321']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual(321, c.b)

    def test_init_cli_override2(self):
        args = ['--b', '321', '--a', '321']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual(321, c.a)
        self.assertEqual(321, c.b)

    def test_init_cli_override3(self):
        args = ['--b.0', '321']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual(321, c.b[0])

    def test_init_cli_override4(self):
        args = ['--d.1.cb', '321']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual(321, c.d[1]['cb'])

    def test_init_cli_override5(self):
        args = ['--f.0.fa.0.faa', '321']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual(321, c.f[0]['fa'][0]['faa'])

    def test_init_cli_override6(self):
        args = ['--a', '[1, 2, 3]']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertListEqual([1, 2, 3], c.a)

    def test_init_cli_override7(self):
        args = ['--a', "{'fa': 1, 'fb': 2, 'fc': 3}"]
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertDictEqual({'fa': 1, 'fb': 2, 'fc': 3}, c.a)

    def test_init_cli_override8(self):
        args = ['--a', 'invalid python expression']
        sys.argv += args

        try:
            c = Config('SAMPLE_01')
        finally:
            for arg in args:
                sys.argv.remove(arg)

        self.assertEqual('invalid python expression', c.a)

    def test_access_attr(self):
        c = Config('SAMPLE_01')
        trg = get_target('SAMPLE_01')

        self.assertEqual(trg['a'], c.a)
        self.assertListEqual(trg['b'], c.b)
        self.assertDictEqual(trg['c'], c.c)
        self.assertListEqual(trg['d'], c.d)
        self.assertDictEqual(trg['e'], c.e)

    def test_access_getter(self):
        c = Config('SAMPLE_01')
        trg = get_target('SAMPLE_01')

        self.assertEqual(trg['a'], c['a'])
        self.assertListEqual(trg['b'], c['b'])
        self.assertDictEqual(trg['c'], c['c'])
        self.assertListEqual(trg['d'], c['d'])
        self.assertDictEqual(trg['e'], c['e'])

    def test_access_get(self):
        c = Config('SAMPLE_01')
        trg = get_target('SAMPLE_01')

        self.assertEqual(trg['a'], c.get('a'))
        self.assertListEqual(trg['b'], c.get('b'))
        self.assertDictEqual(trg['c'], c.get('c'))
        self.assertListEqual(trg['d'], c.get('d'))
        self.assertDictEqual(trg['e'], c.get('e'))
