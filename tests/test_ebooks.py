#!/usr/bin/env python
# encoding: iso-8859-1
import download


__author__ = 'Kennedy Oliveira'

import sys
import unittest

from mock import patch
from workflow import Workflow
import itebooks


class TestEbook(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        # self.wf.reset()
        itebooks.log = self.wf.logger

    def tearDown(self):
        # self.wf.reset()
        pass

    def test_copy_download_link(self):
        with patch.object(sys, 'argv', 'program --copy-download-link 1529159300'.split()):
            ret = itebooks.main(self.wf)
        self.assertEqual(ret, 0)

    def test_open_in_browser(self):
        with patch.object(sys, 'argv', 'program --open-ebook-browser 1529159300'.split()):
            ret = itebooks.main(self.wf)
        self.assertEqual(ret, 0)
        self.assertEqual(len(self.wf._items), 0)

    def test_search_many_words(self):
        with patch.object(sys, 'argv', 'program Elastic Search'.split()):
            ret = itebooks.main(self.wf)
        self.assertEqual(ret, 0)
        self.assertGreater(len(self.wf._items), 0)

    def test_search_with_no_result(self):
        with patch.object(sys, 'argv', 'program Zupao in the mountains'.split()):
            ret = itebooks.main(self.wf)
        self.assertEqual(ret, 1)
        self.assertEqual(len(self.wf._items), 1)

        return_msg = self.wf._items[0].title

        self.assertTrue(return_msg.find('No books found for the query') != -1,
                        'Should return No books found for the query, returned {}'.format(return_msg))

    def test_not_enough_query_character(self):
        with patch.object(sys, 'argv', 'program ja'.split()):
            ret = itebooks.main(self.wf)

        ret_items = self.wf._items
        ret_expected_msg = 'Please, type at least {} characters to start the search...'.format(itebooks.min_characters)

        self.assertTrue(ret, 1)
        self.assertTrue(len(ret_items), 1)
        self.assertTrue(ret_items[0].title == ret_expected_msg)

    def test_show_download_progress(self):
        downloading_books = {}

        books = [('1234', 'Effective Java', 'DOWNLOADING'),
                 ('1235', 'Effective Akka', 'FINISHED'),
                 ('1236', 'Effective POG', 'DOWNLOADING'),
                 ('1237', 'Effective O Primo Basilio', 'DOWNLOADING'),
                 ('1238', 'Os caras que estao falando', 'FINISHED')]

        for book in books:
            downloading_books[book[0]] = {'title': book[0],
                                          'book_id': book[1],
                                          'status': book[2]}

        self.wf.store_data(download.STORED_DOWNLOADING_BOOKS, downloading_books)

        with patch.object(sys, 'argv', 'program --status-download'.split()):
            ret = itebooks.main(self.wf)

        ret_items = self.wf._items

        self.assertEqual(ret, 0)
        self.assertEqual(len(ret_items), 5)

    def test_show_download_progress_no_results(self):
        with patch.object(sys, 'argv', 'program --status-download'.split()):
            ret = itebooks.main(self.wf)

        ret_items = self.wf._items

        self.assertEqual(ret, 1)
        self.assertEqual(len(ret_items), 1)
        self.assertEqual(ret_items[0].title, 'No downloads running at moment.')