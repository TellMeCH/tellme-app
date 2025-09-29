import re
import statistics
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langfuse.decorators import observe
from googleapiclient.discovery import build
from django.conf import settings

from tellme.call_processing.utils import db_handler
from .config import API_MAX_RETRIES, API_BASE_DELAY, API_BACKOFF_FACTOR, MINIMUM_EXPECTED_PRICE, MAXIMUM_EXPECTED_PRICE

class CallValuer:
    """
    CallValuer processes revenue search queries to estimate revenue at stake in customer calls.

    This processor takes a search query, performs a Google Custom Search API query within
    a specific domain, downloads the HTML of the first result, and extracts price information
    to calculate an average revenue value.

    Workflow:
    1. Use Google Custom Search API with site-specific filtering
    2. Get the first relevant product page URL from search results
    3. Download and parse the product page HTML
    4. Extract all price values from the page using regex patterns
    5. Calculate and return average price as revenue estimate

    Attributes:
    max_retries : int
        Maximum number of retry attempts for network requests.
    base_delay : float
        Initial delay between retries in seconds.
    backoff_factor : int
        Multiplier for exponential backoff.
    minimum_price : float
        Minimum price threshold for filtering extracted prices.
    maximum_price : float
        Maximum price threshold for filtering extracted prices.
    search_service : googleapiclient.discovery.Resource
        Google Custom Search API service instance.
    search_engine_id : str
        Custom Search Engine ID for the API.
    """

    def __init__(self):
        """
        Initialize the CallValuer with retry configuration and Google Custom Search API.

        Args:
            max_retries (int): Maximum number of retry attempts for network requests
            base_delay (float): Initial delay between retries in seconds
            backoff_factor (int): Multiplier for exponential backoff
        """

        # Common headers to appear more like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # Initialize Google Custom Search API service
        self.search_service = None
        if hasattr(settings, 'SEARCH_API_KEY') and hasattr(settings, 'SEARCH_ENGINE_ID'):
            try:
                self.search_service = build(
                    "customsearch", "v1", developerKey=settings.SEARCH_API_KEY
                )
                self.search_engine_id = settings.SEARCH_ENGINE_ID
            except Exception as e:
                print(f"Failed to initialize Google Custom Search API: {e}")
                self.search_service = None

    @observe()
    def __call__(self, search_query: str, organization_id: int) -> float:
        """
        Estimate revenue at stake by searching for products and analyzing prices.

        Args:
            search_query (str): Product search query (e.g., "men sneakers", "women dresses")
            organization_id (int): Organization ID to retrieve search prefix

        Returns:
            float: Average price of products found, or None if no prices found or on error

        Raises:
            Exception: Re-raises any unhandled exceptions after logging
        """
        if not search_query or not search_query.strip():
            return None

        # Retrieve the organization's search prefix
        domain_prefix = db_handler.retrieve_organization_search_prefix(organization_id)

        if not domain_prefix or not domain_prefix.strip():
            return None

        try:
            # Get the first relevant product page URL using Google Custom Search API
            product_url = self._get_first_product_url(search_query.strip(), domain_prefix)

            if not product_url:
                return None

            # Download and parse the product page
            prices = self._extract_prices_from_page(product_url)

            if not prices:
                return None

            # Calculate and return average price
            return statistics.mean(prices)

        except Exception as e:
            print(f"CallValuer error processing query '{search_query}': {e}")
            return None

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception_type(Exception)
    )
    def _get_first_product_url(self, search_query: str, domain_prefix: str) -> str:
        """
        Search Google for the query using Custom Search API and return the first result URL.

        Args:
            search_query (str): Product search query (e.g., "men sneakers")
            domain_prefix (str): Domain prefix to restrict search (e.g., "pkz.ch/de/")

        Returns:
            str: URL of first relevant product page, or empty string if none found
        """
        if not self.search_service:
            print("Google Custom Search API not available, skipping search")
            return ""

        try:
            # Use Google Custom Search API with site search restriction
            result = (
                self.search_service.cse()
                .list(
                    q=search_query,
                    cx=self.search_engine_id,
                    siteSearch=domain_prefix,
                    siteSearchFilter="i",  # Include only results from siteSearch
                    num=1  # Only need the first result
                )
                .execute()
            )

            # Check if we have any search results
            if 'items' in result and len(result['items']) > 0:
                first_result = result['items'][0]
                return first_result.get('link', '')

            return ""

        except Exception as e:
            print(f"Google Custom Search API error: {e}")
            return ""

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout))
    )
    def _extract_prices_from_page(self, url: str) -> list[float]:
        """
        Download a webpage and extract all price values from it.

        Args:
            url (str): URL of the product page to analyze

        Returns:
            list[float]: List of price values found on the page
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get all text content from the page
        page_text = soup.get_text()

        # Extract prices using a comprehensive regex pattern
        # This pattern matches all common price formats in a single pass to avoid duplicates
        price_pattern = r'''
            (?:CHF|EUR|€|\$)\s*(\d+(?:[.,]\d{2})?)|  # CHF 199.90, EUR 29.99, €29.99, $49.95
            (\d+(?:[.,]\d{2})?)\s*(?:CHF|EUR|€|\$)|  # 199.90 CHF, 29.99 EUR, 29.99 €, 49.95 $
            \b(\d{2,4}[.,]\d{2})\b|                  # 199.90 or 29,99 (standalone decimals)
            \b(\d{2,4})\.-\b                         # 199.- (Swiss format)
        '''

        prices = []
        # Find all price matches with their positions in the text
        for match in re.finditer(price_pattern, page_text, re.IGNORECASE | re.VERBOSE):
            # Extract the actual price value from the match groups
            price_str = next((group for group in match.groups() if group), None)

            if price_str:
                # Get the context around this price match
                start_pos = max(0, match.start() - 50)  # 50 characters before
                end_pos = min(len(page_text), match.end() + 50)  # 50 characters after
                context = page_text[start_pos:end_pos].lower()

                # Check if this price should be excluded based on context
                exclude_patterns = [
                    r'mindestbestellwert[\:\s]+[^a-zA-Z]*' + re.escape(match.group(0).lower()),
                    r'minimum\s+order[^a-zA-Z]*' + re.escape(match.group(0).lower()),
                    re.escape(match.group(0).lower()) + r'[^a-zA-Z]*(?:rabatt|discount|gutschein)'
                ]

                should_exclude = any(re.search(pattern, context) for pattern in exclude_patterns)

                if not should_exclude:
                    try:
                        # Normalize decimal separators (replace comma with dot)
                        price_str = price_str.replace(',', '.')
                        # Remove any trailing dot and dash (Swiss format)
                        price_str = price_str.rstrip('.-')
                        price = float(price_str)

                        # Filter reasonable price ranges
                        if MINIMUM_EXPECTED_PRICE <= price <= MAXIMUM_EXPECTED_PRICE:
                            prices.append(price)
                    except (ValueError, AttributeError):
                        continue

        return prices