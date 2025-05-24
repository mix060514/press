import scrapy
from datetime import datetime
from press.items import PressItem
from .base_spider import BaseSpider


class NvidiaSpider(BaseSpider):
    name = "nvidia"
    allowed_domains = ["nvidianews.nvidia.com"]
    start_urls = ["https://nvidianews.nvidia.com"]
    url = "https://nvidianews.nvidia.com/news?c=21926&page={}"
    base_url = "https://nvidianews.nvidia.com{}"

    def __init__(self, *args, **kwargs):
        super(NvidiaSpider, self).__init__(*args, **kwargs)
        # NVIDIA-specific pagination
        self.start_page = int(kwargs.get("start_page", 1))
        self.current_page = 1

        # Set up NVIDIA-specific headers
        nvidia_headers = self.get_default_headers()
        nvidia_headers.update(
            {
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "referer": "https://nvidianews.nvidia.com/",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            }
        )

        self.custom_settings.update(
            {
                "DEFAULT_REQUEST_HEADERS": nvidia_headers,
            }
        )

    async def start(self):
        # 直接從第1頁開始
        first_page_url = self.url.format(1)
        yield scrapy.Request(
            url=first_page_url,
            callback=self.parse_menu,
        )

    def parse_menu(self, response):
        # 檢查是否在指定的頁數範圍內
        if self.current_page > self.max_pages:
            self.logger.info(f"Reached maximum pages limit: {self.max_pages}")
            return

        self.logger.info(f"Processing page {self.current_page}")

        # 提取當前頁面的文章連結
        urls = response.css(
            "div#page-content div.container article.index-item div.index-item-text a::attr(href)"
        ).getall()
        for url in urls:
            full_url = self.base_url.format(url)

            # Use base class method to check for crawled URLs
            if self.is_url_crawled(full_url):
                continue

            yield scrapy.Request(
                url=full_url,
                callback=self.parse,
            )
        # 檢查是否還需要繼續爬取下一頁
        if self.current_page < self.max_pages:
            # 增加頁數計數並生成下一頁連結
            self.current_page += 1
            next_page_link = self.url.format(self.current_page)
            yield scrapy.Request(
                url=next_page_link,
                callback=self.parse_menu,
            )

    def parse(self, response):
        title = response.css("div#page-content div.container h1::text").get()
        date = (
            response.css("div#page-content div.container div.article-date::text")
            .get()
            .strip()
        )
        date = datetime.strptime(date, "%B %d, %Y")
        content = response.css(
            "div#page-content div.container div.article-body ::text"
        ).getall()
        content = "\n".join(txt.strip() for txt in content if txt.strip())

        # Log using base class method
        self.log_article_info(title, date, len(content), response.url)

        # Use base class method to create item
        yield self.create_press_item(response.url, title, date, content)
