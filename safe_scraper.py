
# ============================================================
# SAFE & RESPONSIBLE WEB SCRAPER
# ============================================================
#
# Features:
# 1. robots.txt checking
# 2. Timeout
# 3. Status-code checking
# 4. User-Agent
# 5. Delay
# 6. Retry with exponential backoff
# 7. Logging
# 8. Exception handling
#
# ============================================================


import time
import logging
import urllib.robotparser

import requests
from bs4 import BeautifulSoup


# ============================================================
# 1. Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# 2. Configuration
# ============================================================

URL = "https://quotes.toscrape.com/"

TIMEOUT = 10

MAX_RETRIES = 3

DELAY = 2

USER_AGENT = "MyLearningScraper/1.0"


# ============================================================
# 3. Headers
# ============================================================

headers = {
    "User-Agent": USER_AGENT
}


# ============================================================
# 4. Check robots.txt
# ============================================================

def check_robots_txt(url):
    """
    Check whether our scraper is allowed to access the URL
    according to robots.txt.
    """

    try:

        # ----------------------------------------------------
        # Get website base URL
        # ----------------------------------------------------

        parsed_url = requests.utils.urlparse(url)

        base_url = (
            f"{parsed_url.scheme}://{parsed_url.netloc}"
        )


        # ----------------------------------------------------
        # robots.txt URL
        # ----------------------------------------------------

        robots_url = f"{base_url}/robots.txt"

        logger.info(
            f"Checking robots.txt: {robots_url}"
        )


        # ----------------------------------------------------
        # Create robot parser
        # ----------------------------------------------------

        robot_parser = urllib.robotparser.RobotFileParser()

        robot_parser.set_url(robots_url)


        # ----------------------------------------------------
        # Read robots.txt
        # ----------------------------------------------------

        robot_parser.read()


        # ----------------------------------------------------
        # Check permission
        # ----------------------------------------------------

        allowed = robot_parser.can_fetch(
            USER_AGENT,
            url
        )


        if allowed:

            logger.info(
                "robots.txt allows this URL."
            )

            return True

        else:

            logger.warning(
                "robots.txt does not allow this URL."
            )

            return False


    except Exception:

        logger.exception(
            "Error while checking robots.txt."
        )

        return False


# ============================================================
# 5. Fetch Web Page
# ============================================================

def fetch_page(url):

    """
    Download a webpage safely.
    """

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            logger.info(
                f"Request attempt "
                f"{attempt}/{MAX_RETRIES}"
            )


            # ------------------------------------------------
            # Send request
            # ------------------------------------------------

            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT
            )


            # ------------------------------------------------
            # Successful response
            # ------------------------------------------------

            if response.status_code == 200:

                logger.info(
                    "Request successful: HTTP 200"
                )

                return response


            # ------------------------------------------------
            # Not Found
            # ------------------------------------------------

            elif response.status_code == 404:

                logger.warning(
                    "Page not found: HTTP 404"
                )

                return None


            # ------------------------------------------------
            # Forbidden
            # ------------------------------------------------

            elif response.status_code == 403:

                logger.warning(
                    "Access forbidden: HTTP 403"
                )

                return None


            # ------------------------------------------------
            # Too Many Requests
            # ------------------------------------------------

            elif response.status_code == 429:

                logger.warning(
                    "Too many requests: HTTP 429"
                )


            # ------------------------------------------------
            # Server Error
            # ------------------------------------------------

            elif response.status_code >= 500:

                logger.warning(
                    f"Server error: "
                    f"HTTP {response.status_code}"
                )


            # ------------------------------------------------
            # Other status codes
            # ------------------------------------------------

            else:

                logger.warning(
                    f"Unexpected status code: "
                    f"{response.status_code}"
                )

                return None


        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            logger.warning(
                "Request timed out."
            )


        # ----------------------------------------------------
        # Connection error
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            logger.warning(
                "Connection error."
            )


        # ----------------------------------------------------
        # Other requests errors
        # ----------------------------------------------------

        except requests.exceptions.RequestException as e:

            logger.error(
                f"Request error: {e}"
            )


        # ----------------------------------------------------
        # Retry with exponential backoff
        # ----------------------------------------------------

        if attempt < MAX_RETRIES:

            wait_time = DELAY * (2 ** (attempt - 1))

            logger.info(
                f"Waiting {wait_time} seconds..."
            )

            time.sleep(wait_time)


    # --------------------------------------------------------
    # All attempts failed
    # --------------------------------------------------------

    logger.error(
        "All request attempts failed."
    )

    return None


# ============================================================
# 6. Extract Data
# ============================================================

def extract_page_data(response):

    """
    Extract title and text from HTML.
    """

    try:

        # ----------------------------------------------------
        # Parse HTML
        # ----------------------------------------------------

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # ----------------------------------------------------
        # Get title
        # ----------------------------------------------------

        if soup.title:

            title = soup.title.get_text(
                strip=True
            )

        else:

            title = "No title found"


        # ----------------------------------------------------
        # Get page text
        # ----------------------------------------------------

        text = soup.get_text(
            separator=" ",
            strip=True
        )


        return {
            "title": title,
            "text": text
        }


    except Exception:

        logger.exception(
            "Error while parsing HTML."
        )

        return None


# ============================================================
# 7. Main Function
# ============================================================

def main():

    logger.info(
        "Starting safe scraper..."
    )


    # ========================================================
    # Step 1: Check robots.txt
    # ========================================================

    if not check_robots_txt(URL):

        logger.warning(
            "Scraping stopped because robots.txt "
            "does not allow this URL."
        )

        return


    # ========================================================
    # Step 2: Wait before making request
    # ========================================================

    logger.info(
        f"Waiting {DELAY} seconds before request..."
    )

    time.sleep(DELAY)


    # ========================================================
    # Step 3: Fetch webpage
    # ========================================================

    response = fetch_page(URL)


    if response is None:

        logger.error(
            "Could not retrieve webpage."
        )

        return


    # ========================================================
    # Step 4: Extract data
    # ========================================================

    data = extract_page_data(response)


    if data is None:

        logger.error(
            "Could not extract webpage data."
        )

        return


    # ========================================================
    # Step 5: Display result
    # ========================================================

    print("\n" + "=" * 60)

    print("PAGE TITLE:")
    print(data["title"])

    print("\nPAGE TEXT:")

    # Show only first 500 characters
    print(data["text"][:500])

    print("=" * 60)


    logger.info(
        "Scraping completed successfully."
    )


# ============================================================
# 8. Program Entry Point
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        logger.warning(
            "Scraper stopped by user."
        )

    except Exception:

        logger.exception(
            "Unexpected error occurred."
        )

