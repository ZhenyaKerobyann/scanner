import requests, json, os, inspect, tldextract
from future.utils import iteritems
from urllib.parse import urlparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from threading import Thread


class CORSCheck:
    """Class to check for CORS misconfigurations"""
    url = None
    cfg = None
    headers = None
    timeout = None
    result = {}

    def __init__(self, url, cfg):
        self.url = url
        self.cfg = cfg
        self.timeout = cfg["timeout"]
        self.all_results = []
        if cfg["headers"] is not None:
            self.headers = cfg["headers"]
        self.proxies = {}
        if cfg.get("proxy") is not None:
            self.proxies = {
                "http": cfg["proxy"],
                "https": cfg["proxy"],
            }

    def send_req(self, url, origin):
        try:
            headers = {
                'Origin': origin,
                'Cache-Control': 'no-cache',
                'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/59.0.3071.115 Safari/537.36')
            }
            if self.headers is not None:
                headers.update(self.headers)

            self.cfg["logger"].debug(f"Sending request to {self.url} with headers: {headers}")

            # Allow self-signed certificates, follow redirections
            resp = requests.get(
                self.url,
                timeout=self.timeout,
                headers=headers,
                verify=False,
                allow_redirects=True,
                proxies=self.proxies
            )

            self.cfg["logger"].debug(f"Received response: {resp.status_code} {resp.reason}")

            # Remove cross-domain redirections, which may cause false results
            first_domain = tldextract.extract(url).registered_domain
            last_domain = tldextract.extract(resp.url).registered_domain

            if first_domain.lower() != last_domain.lower():
                self.cfg["logger"].debug(
                    f"Cross-domain redirection detected from {first_domain} to {last_domain}"
                )
                resp = None

        except Exception as e:
            self.cfg["logger"].error(f"Exception occurred while sending request: {e}")
            resp = None
        return resp

    def get_resp_headers(self, resp):
        if resp is None:
            return None
        resp_headers = dict((k.lower(), v) for k, v in iteritems(resp.headers))
        return resp_headers

    def check_cors_policy(self, test_module_name, test_origin, test_url):
        resp = self.send_req(self.url, test_origin)
        resp_headers = self.get_resp_headers(resp)
        status_code = resp.status_code if resp is not None else None

        if resp_headers is None:
            self.cfg["logger"].debug(f"No response headers received for origin {test_origin}")
            return None

        self.cfg["logger"].debug(f"Response headers: {resp_headers}")

        acao = resp_headers.get("access-control-allow-origin")
        if acao is None:
            self.cfg["logger"].debug(f"No 'Access-Control-Allow-Origin' header in response for origin {test_origin}")
            return None

        # Determine the allowed origin
        if acao == '*':
            resp_origin = '*'
        elif test_origin != "null":
            parsed = urlparse(acao)
            resp_origin = f"{parsed.scheme}://{parsed.netloc.split(':')[0]}"
        else:
            resp_origin = acao

        msg = None

        # Test if the origin matches (case-insensitive)
        if test_origin.lower() == resp_origin.lower() or resp_origin == '*':
            credentials = "false"

            if resp_headers.get("access-control-allow-credentials") == "true":
                credentials = "true"

            # Construct the message
            msg = {
                "url": test_url,
                "type": test_module_name,
                "credentials": credentials,
                "origin": test_origin,
                "status_code": status_code
            }
            self.cfg["logger"].debug(f"CORS misconfiguration detected: {msg}")
        else:
            self.cfg["logger"].debug(
                f"CORS policy does not allow origin {test_origin}, allowed origin is {resp_origin}"
            )

        return msg

    def is_cors_permissive(self, test_module_name, test_origin, test_url):
        self.cfg["logger"].info(
            f"Testing '{test_module_name}' with origin '{test_origin}' on URL '{test_url}'"
        )
        msg = self.check_cors_policy(test_module_name, test_origin, test_url)

        if msg is not None:
            self.cfg["logger"].warning(f"~Vulnerability found: {msg}")
            self.result = msg
            self.all_results.append(msg)
            return True

        self.cfg["logger"].info(
            f"No vulnerability found for origin '{test_origin}' in test '{test_module_name}'"
        )
        return False

    def test_reflect_origin(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        test_origin = f"{parsed.scheme}://evil.com"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_prefix_match(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        test_origin = f"{parsed.scheme}://{parsed.netloc.split(':')[0]}.evil.com"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_suffix_match(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        sld = tldextract.extract(test_url.strip()).registered_domain
        test_origin = f"{parsed.scheme}://evil{sld}"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_trust_null(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        test_origin = "null"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_include_match(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        sld = tldextract.extract(test_url.strip()).registered_domain
        test_origin = f"{parsed.scheme}://{sld[1:]}"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_not_escape_dot(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        domain = parsed.netloc.split(':')[0]
        test_origin = f"{parsed.scheme}://{domain[::-1].replace('.', 'a', 1)[::-1]}"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_trust_any_subdomain(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        test_origin = f"{parsed.scheme}://evil.{parsed.netloc.split(':')[0]}"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_https_trust_http(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        if parsed.scheme != "https":
            self.cfg["logger"].info(
                f"Skipping test '{module_name}' because URL scheme is not HTTPS"
            )
            return False
        test_origin = f"http://{parsed.netloc.split(':')[0]}"

        self.cfg["logger"].info(
            f"Starting test '{module_name}' on URL '{test_url}' with origin '{test_origin}'"
        )

        return self.is_cors_permissive(module_name, test_origin, test_url)

    def test_custom_third_parties(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url

        self.cfg["logger"].info(f"Starting test '{module_name}' on URL '{test_url}'")

        is_cors_perm = False

        # Opening origins file
        origins_file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '..', 'origins.json'
        )
        try:
            with open(origins_file_path) as origins_file:
                origins = json.load(origins_file)['origins']

                for test_origin in origins:
                    self.cfg["logger"].info(f"Testing origin '{test_origin}'")
                    is_cors_perm = self.is_cors_permissive(module_name, test_origin, test_url)
                    if is_cors_perm:
                        break
        except FileNotFoundError:
            self.cfg["logger"].error(f"Origins file not found at '{origins_file_path}'")

        return is_cors_perm

    def test_special_characters_bypass(self):
        module_name = inspect.stack()[0][3].replace('test_', '')
        test_url = self.url
        parsed = urlparse(test_url)
        special_characters = [
            '_', '-', '"', '{', '}', '+', '^', '%60', '!', '~', '`', ';', '|', '&', "'", '(', ')',
            '*', ',', '$', '=', '+', "%0b"
        ]

        self.cfg["logger"].info(f"Starting test '{module_name}' on URL '{test_url}'")

        origins = []

        for char in special_characters:
            attempt = f"{parsed.scheme}://{parsed.netloc.split(':')[0]}{char}.evil.com"
            origins.append(attempt)

        is_cors_perm = False

        for test_origin in origins:
            self.cfg["logger"].info(f"Testing origin '{test_origin}'")
            is_cors_perm = self.is_cors_permissive(module_name, test_origin, test_url)
            if is_cors_perm:
                break

        return is_cors_perm

    def check_one_by_one(self):
        functions = [
            'test_reflect_origin',
            'test_prefix_match',
            'test_suffix_match',
            'test_trust_null',
            'test_include_match',
            'test_not_escape_dot',
            'test_custom_third_parties',
            'test_special_characters_bypass',
            'test_trust_any_subdomain',
            'test_https_trust_http',
        ]

        self.cfg["logger"].info(f"Starting CORS misconfiguration tests on '{self.url}'")

        for fname in functions:
            self.cfg["logger"].info(f"Running test '{fname}'")
            func = getattr(self, fname)
            if func():
                self.cfg["logger"].info(f"~Vulnerability found in test '{fname}'")
                break

        if not self.result:
            self.cfg["logger"].info("No vulnerabilities found.")

        return self.result

    def check_all_in_parallel(self):
        functions = [
            'test_reflect_origin',
            'test_prefix_match',
            'test_suffix_match',
            'test_trust_null',
            'test_include_match',
            'test_not_escape_dot',
            'test_custom_third_parties',
            'test_special_characters_bypass',
            'test_trust_any_subdomain',
            'test_https_trust_http',
        ]

        self.cfg["logger"].info(f"Starting parallel CORS misconfiguration tests on '{self.url}'")

        threads = []
        for fname in functions:
            func = getattr(self, fname)
            t = Thread(target=func)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if self.all_results:
            self.cfg["logger"].info(f"Vulnerabilities found: {self.all_results}")
        else:
            self.cfg["logger"].info("No vulnerabilities found.")

        return self.all_results
