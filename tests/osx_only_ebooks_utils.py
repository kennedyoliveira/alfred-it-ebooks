#!/usr/bin/env python
# encoding: iso-8859-1

__author__ = 'Kennedy Oliveira'

import unittest

import itebooks


# This tests can't be run from Travis, because use applescript
class TestEbookUtils(unittest.TestCase):
    def test_copy_to_clipboard(self):
        itebooks.copy_to_clipboard('Testing the function.')

    def test_notify(self):
        itebooks.notify('Testing the notify function.')
