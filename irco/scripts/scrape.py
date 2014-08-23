from __future__ import print_function
import argparse
import os
import requests
from irco.logging import sentry, get_logger


DOWNLOAD_URL = 'http://apps.webofknowledge.com/OutboundService.do?action=go'
MAX_RECORDS = 500


# http://wokinfo.com  -- Subscriber login >
# http://sub3.webofknowledge.com/error/Error?PathInfo=%2F&Alias=WOK5&Domain=.webofknowledge.com&Src=IP&RouterURL=http%3A%2F%2Fwww.webofknowledge.com%2F&Error=IPError
# requests.get('http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=Z18u1itzh2szEsmsje8&preferencesSaved=')

# rurl http%3A%2F%2Fapps.webofknowledge.com%2Fsummary.do%3FSID%3DQ2XqL9bU5LfuKsDzQOA%26product%3DUA%26qid%3D2%26search_mode%3DGeneralSearch
# mark_id UDB
# view_name UA-summary
# selectedIds 1;2;3;4;5;6;7;8;9;10
# count_new_items_marked 0
# value(record_select_type) pagerecords
# fields_selection AUTHORSIDENTIFIERS ISSN_ISBN CITTIMES SOURCE TITLE AUTHORS

class AbortDownload(Exception):
    pass


def download(search_id, start, stop, output_stream):
    r = requests.post(DOWNLOAD_URL, stream=True, data={
        'displayCitedRefs': 'true',
        'displayTimesCited': 'true',
        'product': 'WOS',
        'colName': 'WOS',
        'mode': 'OpenOutputService',
        'qid': '2',
        'SID': search_id,
        'format': 'saveToFile',
        'filters': ' '.join([
            # 'USAGEIND',
            # 'AUTHORSIDENTIFIERS',
            'ACCESSION_NUM',
            # 'FUNDING',
            # 'SUBJECT_CATEGORY',
            # 'JCR_CATEGORY',
            # 'LANG',
            # 'IDS',
            # 'PAGEC',
            # 'SABBR',
            # 'CITREFC',
            # 'ISSN',
            # 'PUBINFO',
            # 'KEYWORDS',
            'CITTIMES',
            'ADDRS',
            # 'CONFERENCE_SPONSORS',
            'DOCTYPE',
            # 'CONFERENCE_INFO',
            'SOURCE',
            'TITLE',
            'AUTHORS',
        ]),
        'mark_from': start,
        'mark_to': stop,
        'mark_id': 'UDB',
        'save_options': 'tabMacUTF8',
        'product': 'UA',
        # 'locale': 'en_US',
        # 'view_name': 'WOS-summary',
        # 'search_mode': 'GeneralSearch',

        # Unused fields
        # 'selectedIds': '',
        # 'viewType': 'summary',
        # 'sortBy': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A',
        # 'count_new_items_marked': '0',
        # 'value(record_select_type)': 'range',
        'markFrom': start,
        'markTo': stop,
    })

    if r.headers['content-type'].split(';')[0] != 'text/plain':
        raise AbortDownload()

    gen = r.iter_content(1024)

    for chunk in gen:
        output_stream.write(chunk)


def iterpages(per_page, start=0):
    i = 0
    while True:
        yield i, start
        start += per_page
        i += 1


def main():
    log = get_logger()

    argparser = argparse.ArgumentParser('irco-scrape')
    argparser.add_argument('search_id')
    argparser.add_argument('output')
    argparser.add_argument('count', type=int, nargs='?', help='Deprecated')
    args = argparser.parse_args()

    sentry.context.merge({
        'tags': {'command': 'irco-init'},
        'extra': {'parsed_arguments': args.__dict__}
    })

    log.info('arguments_parsed', args=args)

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    digits = 5

    for i, start in iterpages(MAX_RECORDS):
        dest = os.path.join(args.output, 'savedrecs-{:05d}.csv'.format(i))
        end = start + MAX_RECORDS
        print('{:{}d} - {:{}d} => {}'.format(
            start + 1, digits, end, digits, dest))
        with open(dest, 'wb') as fh:
            try:
                download(args.search_id, start + 1, end, fh)
            except AbortDownload:
                break
    os.remove(dest)
