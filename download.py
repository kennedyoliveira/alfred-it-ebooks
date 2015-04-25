#!/usr/bin/env python
# encoding: iso-8859-1
"""
This script is responsible to download the ebooks from the site.
"""

__author__ = 'Kennedy Oliveira'
__version__ = 'v0.0.1'

import argparse
import os
import sys

import itebooks
from itebooks import STORED_DOWNLOADING_BOOKS
from workflow import Workflow, web


log = None


def main(wf):
    """
    :type wf: Workflow
    """
    log.debug('Initializing download script with args %s', wf.args)

    parser = argparse.ArgumentParser()
    parser.add_argument('--download-from-itebooks', nargs='?', dest='download_itebook')
    parser.add_argument('book_id', nargs='?')
    parser.add_argument('book_title', nargs='*')

    args = parser.parse_args(wf.args)

    if args.download_itebook:
        log.debug('Initializing download')

        downloading_books = wf.stored_data(STORED_DOWNLOADING_BOOKS)

        if not downloading_books:
            downloading_books = {}

        downloading_books[args.book_id] = {'status': 'DOWNLOADING',
                                           'title': ' '.join(args.book_title),
                                           'book_id': args.book_id}

        wf.store_data(STORED_DOWNLOADING_BOOKS, downloading_books)

        try:
            resp = web.get(args.download_itebook, headers={'Referer': 'http://it-ebooks.info'})

            resp.raise_for_status()

            if resp.mimetype != 'application/octet-stream':
                err_msg = 'Error while download {}'.format(args.download_itebook)
                log.error(err_msg)
                itebooks.notify(err_msg)
                return 1

            attachment = resp.headers['content-disposition']

            index = resp.headers['content-disposition'].find('filename=') + 9

            download_folder = os.path.expanduser(itebooks.default_download_folder)

            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            file_name = attachment[index:].replace('"', '')

            file_path = os.path.join(download_folder, file_name)

            with open(file_path, mode='wb') as output:
                itebooks.notify('Starting download of {}'.format(file_name))
                output.write(resp.content)

            itebooks.notify('Download of {} complete!'.format(file_name))
        except:
            return 1
        finally:
            # Update the data for downloading books
            downloading_books[args.book_id]['status'] = 'FINISHED'
            wf.store_data(STORED_DOWNLOADING_BOOKS, downloading_books)
        return 0

    return 0


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))