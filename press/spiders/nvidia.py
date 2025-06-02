import scrapy
from datetime import datetime
from scrapy.shell import inspect_response

class NvidiaSpider(scrapy.Spider):
    name = "nvidia"
    allowed_domains = ["nvidianews.nvidia.com"]
    url_template = "https://nvidianews.nvidia.com/news?c=21926&page={}"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'priority': 'u=0, i',
        'referer': 'https://nvidianews.nvidia.com/news',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    }

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers,
    }

    async def start(self):
        current_page = 1
        yield scrapy.Request(
            url=self.url_template.format(current_page),
            callback=self.parse_listing,
        )
        for current_page in range(2, 3):
            yield scrapy.Request(
                url=self.url_template.format(current_page),
                callback=self.parse_listing,
            )

    def parse_listing(self, response):
        articles = response.css("div#page-content div.container div.index article.index-item")
        for article in articles:
            title = article.css("h3.index-item-text-title a::text").get().strip()
            url = article.css("h3.index-item-text-title a::attr(href)").get()
            # href="/news/nvidia-sets-conference-call-for-first-quarter-financial-results-6910262"
            date = article.css("div.index-item-text div.index-item-text-info span.index-item-text-info-date::text").get()
            # April 30, 2025
            date = datetime.strptime(date, "%B %d, %Y")

            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_article,
                meta={
                    'title': title,
                    'url': url,
                    'date': date,
                }
            )

    def parse_article(self, response):
        # inspect_response(response, self)
        content = response.css("div.conainter div.main div.article-body ::text").getall()
        content = [c.strip() for c in content if c.strip()]
        content = "\n".join(content)
        yield {
            'spider': self.name,
            'title': response.meta['title'],
            'url': response.meta['url'],
            'date': response.meta['date'],
            'content': content,
        }
