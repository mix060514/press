import scrapy
from press.items import PressItem # Import PressItem as it is defined

class IntelSpider(scrapy.Spider):
    name = 'intel'
    allowed_domains = ['newsroom.intel.com', 'intel.com']
    start_urls = ['https://newsroom.intel.com/']

    # Optional: Define custom settings if needed, for example, to set a user-agent
    # custom_settings = {
    #     'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    #     'DOWNLOAD_DELAY': 1, # Be polite by adding a small delay
    # }

    def parse(self, response):
        """
        This method is called to handle the response downloaded for each of the
        requests generated from start_urls. It should identify links to individual
        article pages and generate new Requests for them, specifying parse_article
        as the callback.
        """
        self.logger.info(f"Parsing listing page: {response.url}")

        # TODO: Replace with actual CSS/XPath selectors to find all article links.
        # Example of how to select links:
        # article_links = response.css('div.article-list-item a.read-more::attr(href)').getall()
        # Or, if links are directly on <a> tags within a specific container:
        # article_links = response.css('section#news-releases article h3 a::attr(href)').getall()

        # Placeholder: This selector will likely not work and needs to be replaced.
        # It's a generic example that might find links in common list structures.
        article_links = response.css('article a::attr(href)').getall()

        if not article_links:
            self.logger.warning(f"No article links found on {response.url} with current selectors. Please update the spider's selectors.")

        for link in article_links:
            article_url = response.urljoin(link)
            self.logger.info(f"Found potential article link: {article_url}")
            yield scrapy.Request(article_url, callback=self.parse_article)

        # TODO: Implement pagination if the news listing page has multiple pages.
        # Example for pagination:
        # next_page = response.css('a.next-page-link::attr(href)').get()
        # if next_page is not None:
        #     next_page_url = response.urljoin(next_page)
        #     self.logger.info(f"Found next page: {next_page_url}")
        #     yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        """
        This method is called to handle the response downloaded for an individual
        article page. It should extract the title, date, and content of the article.
        """
        self.logger.info(f"Parsing article page: {response.url}")

        article = PressItem()
        article['url'] = response.url
        article['spider'] = self.name

        # TODO: Replace with actual CSS/XPath selectors for title, date, and content.

        # Example for extracting title:
        # title_selector = 'h1.article-title::text'
        # article['title'] = response.css(title_selector).get()
        # If title might be in a meta tag:
        # article['title'] = response.xpath('//meta[@property="og:title"]/@content').get()
        # Placeholder - this is a very generic selector for a page title.
        # Actual articles will likely have a more specific H1 or meta tag.
        article['title'] = response.css('h1::text').get()
        if not article['title']:
            # Fallback to HTML title tag if H1 is not found or empty
            article['title'] = response.css('title::text').get()
            self.logger.warning(f"Title not found with H1 selector on {response.url}. Used <title> tag instead. Check title selector.")
        if not article['title']:
            self.logger.error(f"Title completely not found on {response.url}. Please define a robust title selector.")
            article['title'] = "Title not found" # Default value

        # Example for extracting date:
        # date_selector = 'span.publication-date::text'
        # raw_date_string = response.css(date_selector).get()
        # Placeholder - this assumes a <time> tag with a datetime attribute.
        # This is a common pattern but might not be present.
        # Other common patterns: <meta property="article:published_time" content="...">
        # or <span class="date">Month Day, Year</span>
        raw_date_string = response.css('time::attr(datetime)').get()
        if not raw_date_string:
            # Fallback example: check for a common meta tag
            # raw_date_string = response.xpath('//meta[@property="article:published_time"]/@content').get()
            self.logger.warning(f"Date not found with <time> selector on {response.url}. Check date selector and consider fallbacks.")
            article['date'] = None # Or a default like datetime.now().isoformat()
        else:
            # TODO: Parse the raw_date_string into a standard format (e.g., YYYY-MM-DD).
            # Example parsing (this is highly dependent on the actual date format found):
            # from datetime import datetime
            # try:
            #   article['date'] = datetime.fromisoformat(raw_date_string.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            # except ValueError:
            #   try:
            #       article['date'] = datetime.strptime(raw_date_string, '%B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
            #   except ValueError:
            #       self.logger.error(f"Could not parse date string: {raw_date_string} on {response.url}")
            #       article['date'] = None # Or keep raw_date_string
            article['date'] = raw_date_string # For now, store the raw string. Parsing needed.


        # Example for extracting content:
        # content_selectors = ['div.article-body *::text', 'div.entry-content *::text']
        # text_parts = []
        # current_selector_texts = []
        # for selector in content_selectors:
        #     current_selector_texts = response.css(selector).getall()
        #     if any(part.strip() for part in current_selector_texts): # Check if list contains non-empty strings
        #         text_parts = current_selector_texts
        #         break
        # article['content'] = "\n".join(part.strip() for part in text_parts if part.strip())
        # Placeholder - gets all text from a common article div, needs refinement
        # This is a very generic selector, actual content is usually in a more specific container.
        content_parts = response.css('div.article-body *::text').getall()
        if not any(part.strip() for part in content_parts): # Check if list is empty or all whitespace
            # Broader fallback if 'div.article-body' yields nothing
            content_parts = response.css('article *::text').getall()
            if not any(part.strip() for part in content_parts):
                 self.logger.warning(f"Content not found on {response.url}. Check content selectors.")

        article['content'] = "\n".join(part.strip() for part in content_parts if part.strip())
        if not article['content']: # Ensure content is not empty string after join
            article['content'] = "Content not found"

        self.logger.info(f"Scraped article fields (raw): Title='{article.get('title', '')}', Date='{article.get('date', '')}', URL='{article.get('url', '')}'")
        yield article
