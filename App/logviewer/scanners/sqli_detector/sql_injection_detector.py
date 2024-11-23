import os

import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set up logging configuration
logging = logging.getLogger('thread_logger')
s = requests.Session()
s.headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
)


def get_all_forms(url):
    """Given a `url`, it returns all forms from the HTML content"""
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):
    """
    This function extracts all possible useful information about an HTML `form`
    """
    details = {}
    try:
        action = form.attrs.get("action").lower()
    except AttributeError:
        action = None
    method = form.attrs.get("method", "get").lower()
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append(
            {"type": input_type, "name": input_name, "value": input_value})
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


def is_vulnerable(response):
    """A function that determines if a page is SQL Injection vulnerable from its `response`"""
    errors = {
        "you have an error in your sql syntax;",
        "warning: mysql",
        "unclosed quotation mark after the character string",
        "quoted string not properly terminated",
        "sql syntax"
    }
    for error in errors:
        if response.status_code == 500 or error in response.content.decode().lower():
            return True
    return False


def main(url):
    logging.info(f"[+] Starting SQL injection scan on {url}")

    # Load payloads from a file in the same directory as the script
    with open(os.path.dirname(os.path.abspath(__file__)) + '/payloads', 'r') as file:
        payloads = file.readlines()

    # Get all forms from the URL
    forms = get_all_forms(url)
    logging.info(f"Detected {len(forms)} forms on {url}.")

    # Track if any vulnerabilities were found
    vulnerability_found = False

    # Check each form for vulnerabilities
    for form in forms:
        form_details = get_form_details(form)
        for payload in payloads:
            data = {}
            for input_tag in form_details["inputs"]:
                if input_tag["value"] or input_tag["type"] == "hidden":
                    data[input_tag["name"]] = input_tag["value"]
                elif input_tag["type"] != "submit":
                    data[input_tag["name"]] = payload.strip()

            # Join the URL with the form's action
            target_url = urljoin(url, form_details["action"])

            # Send the request based on the form method
            if form_details["method"] == "post":
                res = s.post(target_url, data=data)
            elif form_details["method"] == "get":
                res = s.get(target_url, params=data)

            # Check if the response is vulnerable
            if is_vulnerable(res):
                logging.info(f"~SQL Injection vulnerability detected, link: {target_url}")
                logging.info("~Form details:\n~" + str(form_details))
                vulnerability_found = True
                break

    # Log result if no vulnerabilities are found
    if not vulnerability_found:
        logging.info("[+] No SQL Injection vulnerabilities found on this URL.")
    logging.info("[+] SQL Injection completed successfully for target URL.")