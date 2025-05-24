import scrapy
from datetime import datetime
from press.items import PressItem


class BaseSpider(scrapy.Spider):
    """Base spider class for press release crawlers"""

    # Common custom settings
    custom_settings = {
        "ITEM_PIPELINES": {
            "press.pipelines.PressPipeline": 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        # This will be populated by pipeline when spider opens
        self.crawled_urls = set()

        # Common pagination parameters
        self.max_pages = int(kwargs.get("max_pages", 5))
        self.max_results = int(kwargs.get("max_results", 50))

    def is_url_crawled(self, url):
        """Check if URL has already been crawled"""
        if url in self.crawled_urls:
            self.logger.info(f"Skipping already crawled URL: {url}")
            return True
        return False

    def create_press_item(self, url, title, date, content):
        """Create a standardized PressItem"""
        return PressItem(
            spider=self.name,
            url=url,
            title=title.strip() if title else "",
            date=date,
            content=content,
        )

    def get_default_headers(self):
        """Return default headers for requests"""
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "dnt": "1",
            "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        }

    def log_article_info(self, title, date, content_length, url=None):
        """Log standardized article information"""
        title_preview = title[:50] + "..." if len(title) > 50 else title
        self.logger.info(
            f"Processing article: {title_preview} | Date: {date} | Content length: {content_length}"
        )
        if url:
            self.logger.info(f"URL: {url}")

    def log_crawl_summary(self):
        """爬取结束时记录统计信息"""
        self.logger.info(f"=== {self.name} 爬取总结 ===")
        self.logger.info(f"处理页面数: {self.current_page}")
        self.logger.info(f"新文章数: {len(self.items)}")
        self.logger.info(f"跳过重复: {self.skipped_count}")
