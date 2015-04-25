#!/usr/bin/env python
# encoding: iso-8859-1

__author__ = 'Kennedy Oliveira'

import unittest

import itebooks
from workflow import Workflow


class TestEbooksAPI(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.reset()
        itebooks.log = self.wf.logger
        itebooks.wf = self.wf

    def test_search_ebooks(self):
        ebooks_json = itebooks.do_search('java')

        # Validate basic response for the api
        self.assertIsNotNone(ebooks_json)
        self.assertIn('Error', ebooks_json)
        self.assertIn('Time', ebooks_json)
        self.assertIn('Total', ebooks_json)
        self.assertIn('Page', ebooks_json)
        self.assertIn('Books', ebooks_json)
        self.assertTrue(len(ebooks_json['Books']) > 0)

        # Validate ebook info from the api
        ebook = ebooks_json['Books'][0]

        self.assertIn('Description', ebook)
        self.assertIn('ID', ebook)
        self.assertIn('Image', ebook)
        self.assertIn('SubTitle', ebook)
        self.assertIn('Title', ebook)
        self.assertIn('isbn', ebook)

    def test_fetch_many_results(self):
        ebooks_generator = itebooks.search_ebooks('java', 30, self.wf)

        search_result = []

        for ebooks in ebooks_generator:
            search_result.extend(ebooks)

        self.assertIsNotNone(search_result)
        self.assertEqual(len(search_result), 30, 'Wrong fetched result')

    def test_fetch_few_results(self):
        ebooks_generator = itebooks.search_ebooks('Elastic Search', 30, self.wf)

        search_result = []

        for ebooks in ebooks_generator:
            search_result.extend(ebooks)

        self.assertIsNotNone(search_result)
        self.assertLess(len(search_result), 10, 'Wrong fetched results')
        self.assertGreater(len(search_result), 0, 'Wrong fetched results')

    def test_get_ebook_info(self):
        ebook_info = itebooks.get_ebook_info(1529159300)

        self.assertIsNotNone(ebook_info)
        self.assertIsInstance(ebook_info, dict, 'Not a dictionary')
        self.assertIn('Author', ebook_info)
        self.assertIn('Description', ebook_info)
        self.assertIn('Download', ebook_info)
        self.assertIn('Error', ebook_info)
        self.assertIn('ID', ebook_info)
        self.assertIn('ISBN', ebook_info)
        self.assertIn('Image', ebook_info)
        self.assertIn('Page', ebook_info)
        self.assertIn('SubTitle', ebook_info)
        self.assertIn('Time', ebook_info)
        self.assertIn('Title', ebook_info)
        self.assertIn('Year', ebook_info)
        self.assertEqual(ebook_info['Error'], u'0')

    def test_ebook_not_found(self):
        ebook_info = itebooks.get_ebook_info(-1)

        self.assertIsNotNone(ebook_info)
        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].subtitle, 'Book not found!')