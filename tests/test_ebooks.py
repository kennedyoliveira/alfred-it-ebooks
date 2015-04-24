#!/usr/bin/env python
# encoding: iso-8859-1


__author__ = 'Kennedy Oliveira'

import sys
import unittest

from mock import patch

from workflow import Workflow
import itebooks


class TestEbook(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        itebooks.log = self.wf.logger

    def test_copy_download_link(self):
        with patch.object(sys, 'argv', 'program --copy-download-link 1529159300'.split()):
            ret = itebooks.main(self.wf)
        self.assertEqual(ret, 0)