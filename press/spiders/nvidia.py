import scrapy

from datetime import datetime
from press.items import PressItem


class NvidiaSpider(scrapy.Spider):
    name = "nvidia"
    allowed_domains = ["nvidianews.nvidia.com"]
    start_urls = ["https://nvidianews.nvidia.com"]
    url = "https://nvidianews.nvidia.com/news?c=21926"
    base_url = "https://nvidianews.nvidia.com{}"
    

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'priority': 'u=0, i',
        'referer': 'https://nvidianews.nvidia.com/',
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
    custom_settings = {
            'DEFAULT_REQUEST_HEADERS': headers

    }


    async def start(self):
        yield scrapy.Request(
            url=self.url,
            callback=self.parse_menu,
        )
    def parse_menu(self, response):
        urls = response.css("div#page-content div.container article.index-item div.index-item-text a::attr(href)").getall()
        for url in urls:
            yield scrapy.Request(
                url=self.base_url.format(url),
                callback=self.parse,
            )

    def parse(self, response):
        title = response.css("div#page-content div.container h1::text").get()
        date = response.css("div#page-content div.container div.article-date::text").get().strip()
        date = datetime.strptime(date, "%B %d, %Y")
        content = response.css("div#page-content div.container div.article-body ::text").getall()
        content = '\n'.join(txt.strip() for txt in content if txt.strip())
        yield PressItem(
            spider=self.name,
            url=response.url,
            title=title,
            date=date,
            content=content,
        )
