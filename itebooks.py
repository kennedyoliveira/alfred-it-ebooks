#!/usr/bin/env python
# encoding: iso-8859-1
"""
A workflow for searching and download IT eBooks from the IT-eBooks Library.
"""

__author__ = 'Kennedy Oliveira'
__version__ = 'v0.0.1'

import argparse
import os
import sys
import webbrowser

from workflow import Workflow, web, background, ICON_ERROR, ICON_WARNING


class SearchException(Exception):
    pass


log = None

# URL for searching books
search_url = 'http://it-ebooks-api.info/v1/search/'

# URL for getting book info
ebook_info_url = 'http://it-ebooks-api.info/v1/book/'

# The minimum characters to type for searching
min_characters = 3

# How many ebooks to show per search, each request to the api return 10 books, but you can configure to show more
ebooks_per_search = 30

# Default download folder
default_download_folder = '~/Downloads'

# Key for the dict holding the downloading books in the moment
STORED_DOWNLOADING_BOOKS = 'it_ebooks_downloading'


def get_ebook_info(ebook_id):
    """
    Get the ebook info based with the ebook ID

    :param ebook_id: ID of the ebook to search the info
    """
    resp = web.get(ebook_info_url + str(ebook_id), timeout=10)

    resp.raise_for_status()

    json = resp.json()

    if json['Error'] != '0':
        wf.add_item('Error on getting ebook info', json['Error'], icon=ICON_ERROR)
        wf.send_feedback()
        return 2

    return json


def search_ebooks(query, total_results, wf):
    """
    Generator function to search for the query trying to fetch as many ebooks as total_results

    :param query: Query to be used to fetch ebooks
    :param total_results: Total of ebooks to try to fetch
    :type wf: Workflow
    """
    if total_results is None or total_results < 0:
        raise StopIteration()

    for page in range(1, (total_results / 10) + 1):
        def search_wrapper():
            return do_search(query, page)

        try:
            json = wf.cached_data('{}{}'.format(query, page), search_wrapper, max_age=60 * 60)
        except SearchException:
            break

        # Means there are more pages
        if json and int(json['Total']) > 10:
            yield json['Books']
        else:
            break


def do_search(query, page=None):
    """
    Search for the query with the specified page or the first one if None is specified

    :rtype : dict
    """
    log.debug('Starting searching for [%s]', query)

    # Gets the first page
    if not page:
        r = web.get(search_url + query, timeout=10)
    else:
        # Gets the specified page
        r = web.get("{}{}/page/{}".format(search_url, query, page), timeout=10)

    r.raise_for_status()

    json = r.json()

    if json['Error'] != u'0':
        wf.add_item('Erro on searching', str(json['Error']), icon=ICON_ERROR)
        wf.send_feedback()
        raise SearchException('Error or searching')

    log.debug('No errors on search')

    return json


def copy_to_clipboard(text):
    """
    Copy the text to the clipboard

    :param text: Text to be copied to the clipboard
    """
    os.system(r'osascript -e "set the clipboard to \"{}\""'.format(text))


def notify(text):
    """
    Call this workflow to show a notification.

    :param text: Text for the notification.
    """
    script = 'tell application \\"Alfred 2\\" to run trigger \\"echo_notify\\" ' \
             'in workflow \\"com.razor.itbooks\\" with argument \\"{}\\"'.format(text)

    os.system(r'osascript -e "{}"'.format(script))


def main(wf):
    """

    :type wf: Workflow
    """
    log.debug('Iniciando o script ...')
    log.debug('Args received %s', wf.args)

    parser = argparse.ArgumentParser()

    parser.add_argument('--open-ebook-browser', nargs='?', default=None, dest='open_in_browser')
    parser.add_argument('--copy-download-link', nargs='?', default=None, dest='copy_download_link')
    parser.add_argument('--download-ebook', nargs='?', default=None, dest='download_ebook')
    parser.add_argument('--status-download', default=None, dest='status_download', action='store_true')
    parser.add_argument('query', nargs='*', default=None)
    args = parser.parse_args(wf.args)

    ##########################################################################################
    # Open the download link on the browser
    ##########################################################################################
    if args.open_in_browser:
        ebook_info = get_ebook_info(args.open_in_browser)

        # Error on getting book info
        if type(ebook_info) == int:
            return ebook_info

        webbrowser.open(ebook_info['Download'], 1)
        return 0

    ##########################################################################################
    # Copy the download link to clipboard
    ##########################################################################################
    if args.copy_download_link:
        log.debug('Coping the download link for ebook %s', args.copy_download_link)
        ebook_info = get_ebook_info(args.copy_download_link)

        if type(ebook_info) == int:
            return ebook_info

        copy_to_clipboard(ebook_info['Download'])

        print 'Copied Download link for the book {}'.format(ebook_info.get('Title', 'No name'))
        return 0

    ##########################################################################################
    # Download the ebook to the downloads folder
    ##########################################################################################
    if args.download_ebook:
        log.debug('Downloading ebook id - %s', args.download_ebook)

        ebook_info = get_ebook_info(args.download_ebook)

        if type(ebook_info) == int:
            return ebook_info

        daemon_download = 'ite_ebook_download_{}'.format(args.download_ebook)

        if background.is_running(daemon_download):
            log.debug('Ebook %s is already downloading', args.download_ebook)
            wf.add_item('This ebook is already beaing downloaded.',
                        'Please, wait this ebook to finish or cancel its download before trying again.')
            wf.send_feedback()
            return 1

        background.run_in_background(daemon_download,
                                     ['/usr/bin/env',
                                      'python',
                                      wf.workflowfile('download.py'),
                                      '--download-from-itebooks',
                                      ebook_info['Download'],
                                      args.download_ebook,
                                      ebook_info['Title']])
        return 0

    ##########################################################################################
    # Show the progress and status of the downloads
    ##########################################################################################
    if args.status_download:
        downloads = wf.stored_data(STORED_DOWNLOADING_BOOKS)

        if not downloads:
            wf.add_item('No downloads running at moment.')
            wf.send_feedback()
            return 0

        for ebooks_id, download in downloads.iteritems():
            wf.add_item(download['title'], 'Status: {}'.format(download['status']))
        wf.send_feedback()

        return 0

    ##########################################################################################
    # Check if the user typed the data needed
    ##########################################################################################
    if not args.query or len(args.query[0]) < min_characters:
        log.debug('Not enough args or characters ...')
        msg = 'Please, type at least {} characters to start the search...'.format(min_characters)
        wf.add_item(msg, icon=ICON_WARNING)
        wf.send_feedback()
        return 1

    ##########################################################################################
    # Search for the books
    ##########################################################################################
    if args.query:
        query = args.query[0]

        ebook_generator = search_ebooks(query, ebooks_per_search, wf)

        ebooks_found = 0

        for ebooks in ebook_generator:
            for ebook in ebooks:
                ebooks_found += 1
                title = ebook.get('Title', 'No Title')
                subtitle = ebook.get('SubTitle', ebook.get('Description', 'No subtitle'))
                isbn = ebook.get('isbn', 'No ISBN')
                book_id = str(ebook['ID'])

                wf.add_item(title, subtitle, uid=isbn, arg=book_id, valid=True)
        wf.send_feedback()

        if ebooks_found == 0:
            wf.add_item('No books found for the query: {}'.format(query), icon=ICON_WARNING)
            wf.send_feedback()
            return 1

        log.debug("End of it-ebooks")
    else:
        wf.add_item('Invalid args...', icon=ICON_ERROR)
        wf.send_feedback()
        return 1


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))