import requests
import logging
import time
from .parsing import format_seconds

def make_retry_request(url, tries=10, retry_delay=5, headers={}):
    for attempt in range(tries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return response, data 
            elif response.status_code == 503: 
                # Retry on 503 status code
                print(err := f"Reason: {response.headers.get('message')}")
                logging.warning(err)
                delay = retry_delay*(attempt) + 1
                logging.warning(f"Received 503. Retrying in {format_seconds(delay)} (attempt {attempt + 1}/{tries})")
                time.sleep(delay)
            else:
                print(err := f"Failed to fetch data: HTTP Status {response.status_code}")
                logging.error(err)
        except requests.RequestException as e:
            logging.error(f"Network error during data fetch: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
    return None, None