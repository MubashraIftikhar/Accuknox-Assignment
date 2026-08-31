#!/usr/bin/env python3
"""
Application Health Checker
---------------------------
Checks whether a web application is 'up' or 'down' by making an HTTP(S)
request and inspecting the status code. Handles self-signed TLS certs
(like the one used for the Wisecow app) via --insecure.

Usage:
    python3 app_health_checker.py https://wisecow.local:8443 --insecure
    python3 app_health_checker.py https://example.com
    python3 app_health_checker.py https://wisecow.local:8443 --insecure --watch 10

Dependencies:
    pip install requests --break-system-packages
"""

import argparse
import datetime
import os
import sys
import time

try:
    import requests
    import urllib3
except ImportError:
    print("ERROR: 'requests' is not installed. Run: pip install requests --break-system-packages")
    sys.exit(1)

LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_health.log")

# 'Up' = any 2xx or 3xx status code (server responded normally)
# 'Down' = 4xx, 5xx, timeout, or connection error
UP_STATUS_RANGE = range(200, 400)


def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_line(message):
    line = f"[{timestamp()}] {message}"
    print(line)
    with open(LOG_FILE_PATH, "a") as f:
        f.write(line + "\n")


def check_url(url, verify_ssl=True, timeout=5):
    """
    Sends a GET request to the URL and returns a (status, detail) tuple.
    status is either 'UP' or 'DOWN'.
    """
    try:
        response = requests.get(url, timeout=timeout, verify=verify_ssl)
        if response.status_code in UP_STATUS_RANGE:
            return "UP", f"HTTP {response.status_code}"
        else:
            return "DOWN", f"HTTP {response.status_code} (error status)"
    except requests.exceptions.SSLError as e:
        return "DOWN", f"SSL error: {e}"
    except requests.exceptions.ConnectionError:
        return "DOWN", "Connection error (host unreachable / refused)"
    except requests.exceptions.Timeout:
        return "DOWN", f"Timed out after {timeout}s"
    except requests.exceptions.RequestException as e:
        return "DOWN", f"Request failed: {e}"


def run_check(url, verify_ssl):
    status, detail = check_url(url, verify_ssl=verify_ssl)
    log_line(f"{url} -> {status} ({detail})")
    return status


def main():
    parser = argparse.ArgumentParser(description="Check if a web application is up or down.")
    parser.add_argument("url", help="URL of the application to check, e.g. https://wisecow.local:8443")
    parser.add_argument("--insecure", action="store_true",
                         help="Skip TLS certificate verification (needed for self-signed certs).")
    parser.add_argument("--watch", type=int, metavar="SECONDS",
                         help="Check repeatedly every SECONDS seconds until Ctrl+C.")
    args = parser.parse_args()

    if args.insecure:
        # Suppress the "InsecureRequestWarning" noise since we're doing this deliberately
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    verify_ssl = not args.insecure

    print(f"Checking: {args.url}")
    print(f"Logging to: {LOG_FILE_PATH}\n")

    if args.watch:
        try:
            while True:
                run_check(args.url, verify_ssl)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped by user.")
    else:
        run_check(args.url, verify_ssl)


if __name__ == "__main__":
    main()
