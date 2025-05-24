import scrapy
import json
from datetime import datetime
from press.items import PressItem
from .base_spider import BaseSpider


class AmdSpider(BaseSpider):
    name = "amd"
    allowed_domains = ["www.amd.com", "xilinxcomprode2rjoqok.org.coveo.com"]

    # API endpoint instead of HTML page
    api_url = "https://xilinxcomprode2rjoqok.org.coveo.com/rest/search/v2"
    base_url = "https://www.amd.com{}"

    def __init__(self, *args, **kwargs):
        super(AmdSpider, self).__init__(*args, **kwargs)

        # AMD-specific pagination parameters
        self.results_per_page = int(
            kwargs.get("results_per_page", 12)
        )  # Results per API call
        self.current_offset = 0  # Current offset for pagination

        # Set up AMD-specific headers
        amd_headers = self.get_default_headers()
        amd_headers.update(
            {
                "authorization": "Bearer xx5ee91b6a-e227-4c6f-83f2-f2120ca3509e",
                "content-type": "application/json",
                "origin": "https://www.amd.com",
                "priority": "u=1, i",
                "referer": "https://www.amd.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }
        )

        self.custom_settings.update(
            {
                "DEFAULT_REQUEST_HEADERS": amd_headers,
            }
        )

    def start_requests(self):
        """Start with API request instead of HTML page"""
        yield self.make_api_request(first_result=0)

    def make_api_request(self, first_result=0):
        """Create API request with proper payload"""
        params = {
            "organizationId": "xilinxcomprode2rjoqok",
        }

        json_data = {
            "locale": "en",
            "debug": False,
            "tab": "default",
            "referrer": "default",
            "timezone": "Asia/Taipei",
            "cq": '(@amd_result_type=="Press Releases")',
            "context": {
                "amd_lang": "en",
            },
            "fieldsToInclude": [
                "author",
                "language",
                "urihash",
                "objecttype",
                "collection",
                "source",
                "permanentid",
                "date",
                "filetype",
                "parents",
                "amd_result_type",
                "amd_release_date",
                "amd_lang",
                "amd_result_image",
                "description",
                "amd_partner",
                "amd_cta_link",
                "amd_category",
                "amd_product_category",
                "amd_region",
                "amd_product_brand",
                "amd_product_type",
                "amd_industries",
            ],
            "q": "",
            "enableQuerySyntax": False,
            "searchHub": "press-releases-sh",
            "sortCriteria": "@amd_release_date descending",
            "queryCorrection": {
                "enabled": False,
                "options": {
                    "automaticallyCorrect": "whenNoResults",
                },
            },
            "enableDidYouMean": True,
            "facets": [
                {
                    "filterFacetCount": True,
                    "injectionDepth": 1000,
                    "numberOfValues": 8,
                    "sortCriteria": "alphanumeric",
                    "resultsMustMatch": "atLeastOneValue",
                    "type": "specific",
                    "currentValues": [],
                    "freezeCurrentValues": False,
                    "isFieldExpanded": False,
                    "preventAutoSelect": False,
                    "facetId": "amd_press_category",
                    "field": "amd_press_category",
                }
            ],
            "numberOfResults": self.results_per_page,
            "firstResult": first_result,
            "facetOptions": {
                "freezeFacetOrder": False,
            },
        }

        return scrapy.Request(
            url=self.api_url,
            method="POST",
            headers=self.custom_settings["DEFAULT_REQUEST_HEADERS"],
            body=json.dumps(json_data),
            callback=self.parse_api_response,
            meta={"first_result": first_result},
            dont_filter=True,
        )

    def parse_api_response(self, response):
        """Parse API response and extract press release data"""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return

        results = data.get("results", [])
        total_count = data.get("totalCount", 0)
        first_result = response.meta.get("first_result", 0)

        self.logger.info(
            f"Processing {len(results)} results from offset {first_result}"
        )
        self.logger.info(f"Total available results: {total_count}")

        for result in results:
            # Extract URL from the result
            url = result.get("uri", "") or result.get("clickUri", "")
            if not url:
                continue

            # Use base class method to check for crawled URLs
            if self.is_url_crawled(url):
                continue

            # Extract comprehensive information from API response
            title = result.get("title", "")
            excerpt = result.get("excerpt", "")

            # Extract from raw data section
            raw_data = result.get("raw", {})
            raw_date = raw_data.get("amd_release_date")
            result_image = raw_data.get("amd_result_image", "")
            document_location = raw_data.get("amd_document_location", "")
            result_type = raw_data.get("amd_result_type", "")
            language = raw_data.get("language", [])

            # Also check for description in the main result object
            description = result.get("description", "") or excerpt

            # Parse date from timestamp
            date = None
            if raw_date:
                try:
                    # API returns timestamp in milliseconds
                    if isinstance(raw_date, (int, float)):
                        date = datetime.fromtimestamp(raw_date / 1000)
                    elif isinstance(raw_date, str):
                        # Try to parse as ISO format or other common formats
                        if "T" in raw_date:
                            date = datetime.fromisoformat(
                                raw_date.replace("Z", "+00:00")
                            )
                except Exception as e:
                    self.logger.warning(f"Could not parse date '{raw_date}': {e}")

            # Log extracted information for debugging
            self.logger.info(f"Extracted: {title[:50]}... | Date: {date} | URL: {url}")

            # Make request to individual article page for full content
            yield scrapy.Request(
                url=url,
                callback=self.parse_article,
                meta={
                    "api_title": title,
                    "api_date": date,
                    "api_description": description,
                    "api_excerpt": excerpt,
                    "api_result_image": result_image,
                    "api_document_location": document_location,
                    "api_result_type": result_type,
                    "api_language": language,
                    "api_raw_date": raw_date,
                },
            )

        # Check if we need to fetch more results
        next_first_result = first_result + len(results)
        if next_first_result < total_count and next_first_result < self.max_results:
            self.logger.info(f"Fetching next batch starting from {next_first_result}")
            yield self.make_api_request(first_result=next_first_result)

    def parse_article(self, response):
        # Get API data from meta as fallback
        title = response.meta.get("api_title", "")
        date = response.meta.get("api_date")

        # 提取文章內容
        content: list[str] = response.css(
            "div.article-container div.text ::text"
        ).getall()
        content = "\n".join(txt.strip() for txt in content if txt.strip())

        # Log using base class method
        self.log_article_info(title, date, len(content), response.url)

        # Use base class method to create item
        yield self.create_press_item(response.url, title, date, content)
