import scrapy
from datetime import datetime
from press.items import PressItem
from .base_spider import BaseSpider


class IntelSpider(BaseSpider):
    name = "intel"
    allowed_domains = ["newsroom.intel.com"]
    start_urls = ["https://newsroom.intel.com"]
    start_url = "https://newsroom.intel.com/all-news/page/{}"
    base_url = "https://newsroom.intel.com{}"

    def __init__(self, *args, **kwargs):
        super(IntelSpider, self).__init__(*args, **kwargs)
        # Intel-specific pagination
        self.start_page = int(kwargs.get("start_page", 1))
        self.current_page = 0
        self.items = []
        self.skipped_count = 0

        # Set up Intel-specific headers
        intel_headers = self.get_default_headers()
        intel_headers.update(
            {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'dnt': '1',
                'priority': 'u=0, i',
                'referer': 'https://newsroom.intel.com/',
                'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            }
        )

        self.custom_settings.update(
            {
                "DEFAULT_REQUEST_HEADERS": intel_headers,
            }
        )

    def start_requests(self):
        # Start from the first page
        first_page_url = self.start_url.format(self.start_page)
        self.current_page = self.start_page
        yield scrapy.Request(
            url=first_page_url,
            callback=self.parse_menu,
        )

    def parse_menu(self, response):
        self.logger.info(f"Processing page {self.current_page}")
        
        articles = response.css("div#primary main#main div#post-wrap div.post-result-item-container")
        for article in articles:
            link = article.css("a.post-result-item::attr(href)").get()
            title = article.css("div h2::text").get()
            date = article.css("p.item-post-date::text").get()
            date = date.strip()
            date = date.replace("Updated ", "")
            date = datetime.strptime(date, "%B %d, %Y")

            if self.is_url_crawled(link):
                continue

            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={"date": date, "title": title}
            )

        # Check if we need to continue to the next page
        if self.current_page < self.max_pages:
            # Increase page count and generate next page link
            self.current_page += 1
            next_page_link = self.start_url.format(self.current_page)
            yield scrapy.Request(
                url=next_page_link,
                callback=self.parse_menu,
            )
        else:
            self.log_crawl_summary()

    def parse_article(self, response):
        title = response.meta.get("title")
        date = response.meta.get("date")
        content = response.css("div.entry-content-wrapper div.entry-content ::text").getall()
        content = "\n".join(txt.strip() for txt in content if txt.strip())
        
        # Log using base class method
        self.log_article_info(title, date, len(content) if content else 0, response.url)

        # Create and yield the item
        item = self.create_press_item(response.url, title, date, content)
        yield item 
