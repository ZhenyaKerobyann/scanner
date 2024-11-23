import threading
from queue import Queue
from colorama import init
import logging
from common.common import parse_headers, read_urls
from common.corscheck import CORSCheck

# Set up logging
logger = logging.getLogger('thread_logger')

# Globals
results = []
c = threading.Condition()


def scan(cfg):
    global results

    while not cfg["queue"].empty():
        try:
            item = cfg["queue"].get(timeout=1.0)
            cors_check = CORSCheck(item, cfg)
            msg = cors_check.check_one_by_one()

            # Keeping results to be written to file only if needed
            if msg:
                with c:
                    results.append(msg)
                logger.info(f"Processed item: {item}")
        except Exception as e:
            logger.error(f"Error processing item: {item} - {e}", exc_info=True)
            break


def cors_check(url, headers=None):
    cfg = {"logger": logger, "headers": headers, "timeout": 5}

    cors_check = CORSCheck(url, cfg)
    msg = cors_check.check_one_by_one()
    return msg


def main(url):
    init()
    queue = Queue()

    # Configuration for the CORS check
    cfg = {
        "logger": logger,
        "queue": queue,
        "headers": parse_headers(None),
        "timeout": 10,
        "proxy": {}
    }

    # Populate queue with URLs
    read_urls(url, '', queue)

    logger.info("[+]Starting CORS scan...")

    try:
        scan(cfg)
    except KeyboardInterrupt:
        logger.warning("CORS scan interrupted by user.")
    finally:
        logger.info("Finished CORS scanning.")
