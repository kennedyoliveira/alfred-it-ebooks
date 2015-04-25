#!/usr/bin/env python
# encoding: iso-8859-1
import os

import itebooks


__author__ = 'Kennedy Oliveira'

import sys
import unittest

import download
from workflow import Workflow
from mock import patch


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.reset()
        download.log = self.wf.logger

    def test_download(self):
        download_link = 'http://filepi.com/i/RSpHA1T'
        ebook_id = '1529159300'
        ebook_title = 'Expert Oracle and Java Security'

        args = 'program --download-from-itebooks {} {} {}'.format(download_link, ebook_id, ebook_title).split()

        with patch.object(sys, 'argv', args):
            ret = download.main(self.wf)

        download_folder = os.path.expanduser(itebooks.default_download_folder)

        file_name = 'Expert Oracle and Java Security.pdf'

        file_path = os.path.join(download_folder, file_name)

        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(file_path))