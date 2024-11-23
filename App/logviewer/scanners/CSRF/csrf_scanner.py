import requests
import logging
from bs4 import BeautifulSoup

# Set up logging configuration
logging = logging.getLogger('thread_logger')


def main(url):
    logging.info(f"[+] Starting CSRF scan on {url}")
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        logging.info('No valid URLs to test.')
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    forms = soup.find_all(
        'form', {'method': lambda x: x and 'post' in x.lower()}
    )
    if not forms:
        logging.info(f"No forms found on {url}.")
        return

    for form in forms:
        csrf_inputs = form.find_all(
            'input', {'name': lambda x: x and 'csrf' in x.lower()}
        )
        if not csrf_inputs:
            logging.info(f"~Potential CSRF vulnerability found in form on {url}")
        else:
            logging.info(f"CSRF token found in form on {url}, form is secure.")

    logging.info("CSRF verification complete for all forms on the page.")
