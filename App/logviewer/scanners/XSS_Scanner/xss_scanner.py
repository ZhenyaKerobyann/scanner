import concurrent.futures
from urllib.parse import urlparse
import sys
import json

sys.path.append('./logviewer/scanners/XSS_Scanner')

from core.config import blindPayload
from core.photon import photon
from core.utils import reader

from modes.crawl import crawl

from core.config import headers
import core.config
import core.log

# Pull all parameter values of dict from argparse namespace into local variables of name == key
# The following works, but the static checkers are too static ;-) locals().update(vars(args))
update = ''
timeout = core.config.timeout
proxy = ''
level = 3
add_headers = True
threadCount = core.config.threadCount
delay = core.config.delay
skip = ''
skipDOM = ''
blindXSS = ''

logger = core.log.setup_logger()


def main(target):
    core.config.globalVariables = {'target': target, 'path': '', 'jsonData': '',
                                   'paramData': '', 'encode': '', 'fuzz': '', 'update': '',
                                   'timeout': core.config.timeout,
                                   'proxy': '', 'recursive': '', 'args_file': '', 'args_seeds': '',
                                   'level': core.log.console_log_level, 'add_headers': True,
                                   'threadCount': core.config.threadCount, 'delay': core.config.delay, 'skip': '',
                                   'skipDOM': '', 'blindXSS': '', 'headers': headers, 'checkedScripts': set(),
                                   'checkedForms': {},
                                   'definitions': json.loads(
                                       '\n'.join(reader('./logviewer/scanners/XSS_Scanner' + '/db/definitions.json')))}
    core.config.proxies = {}

    logger.run('Crawling the target')
    scheme = urlparse(target).scheme
    logger.debug('Target scheme: {}'.format(scheme))
    host = urlparse(target).netloc
    main_url = scheme + '://' + host
    crawlingResult = photon(target, headers, level,
                            threadCount, delay, timeout, skipDOM)
    forms = crawlingResult[0]
    domURLs = list(crawlingResult[1])
    difference = abs(len(domURLs) - len(forms))
    if len(domURLs) > len(forms):
        for i in range(difference):
            forms.append(0)
    elif len(forms) > len(domURLs):
        for i in range(difference):
            domURLs.append(0)
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(crawl, scheme, host, main_url, form,
                                 blindXSS, blindPayload, headers, delay, timeout, False) for form, domURL in
               zip(forms, domURLs))
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        if i + 1 == len(forms) or (i + 1) % threadCount == 0:
            logger.info('Progress: %i/%i\r' % (i + 1, len(forms)))
    logger.info('XSS scan completed successfully for target URL')


if __name__ == '__main__':
    main('http://127.0.0.1:8080/')
