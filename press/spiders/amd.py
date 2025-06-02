import scrapy
import json
from datetime import datetime
from press.items import PressItem
from scrapy.shell import inspect_response

params = {
    'organizationId': 'xilinxcomprode2rjoqok',
}

json_data = {
    'locale': 'en',
    'debug': False,
    'tab': 'default',
    'referrer': 'https://www.amd.com/en/newsroom.html',
    'timezone': 'Asia/Taipei',
    'cq': '(@amd_result_type=="Press Releases")',
    'context': {
        'amd_lang': 'en',
    },
    'fieldsToInclude': [
        'author',
        'language',
        'urihash',
        'objecttype',
        'collection',
        'source',
        'permanentid',
        'date',
        'filetype',
        'parents',
        'ec_price',
        'ec_name',
        'ec_description',
        'ec_brand',
        'ec_category',
        'ec_item_group_id',
        'ec_shortdesc',
        'ec_thumbnails',
        'ec_images',
        'ec_promo_price',
        'ec_in_stock',
        'ec_rating',
        'amd_result_type',
        'amd_release_date',
        'amd_lang',
        'amd_result_image',
        'limessageissolution',
        'lithreadhassolution',
        'description',
        'amd_partner',
        'amd_cta_link',
        'amd_hub_pull_command',
        'amd_child_design_file',
        'amd_child_associated_file',
        'amd_video_date',
        'amd_video_duration',
        'amd_video_views',
        'ytlikecount',
        'amd_document_id',
        'amd_document_type',
        'amd_document_location',
        'amd_claim_text',
        'amd_cert_driver_app_name',
        'amd_cert_driver_app_version',
        'amd_cert_driver_brand_name',
        'amd_cert_driver_isv',
        'amd_cert_driver_name',
        'amd_cert_driver_os',
        'amd_cert_driver_url',
        'amd_cert_driver_video_card',
        'amd_support_article_type',
        'amd_app_type',
        'amd_category',
        'amd_product_category',
        'amd_supported_workloads',
        'amd_target_platforms',
        'amd_product_vendor',
        'amd_vendor_type',
        'amd_is_external_link',
        'amd_hub_container',
        'amd_region',
        'workphone',
        'amd_product_brand',
        'amd_product_type',
        'amd_w2buy_partner_type',
        'amd_industries',
        'amd_application_specialty',
        'amd_product_price',
        'amd_partner_tier',
        'amd_product_sub_category',
        'amd_open_source_project_interest',
        'amd_cta_link_2',
    ],
    'q': '',
    'enableQuerySyntax': False,
    'searchHub': 'press-releases-sh',
    'sortCriteria': '@amd_release_date descending',
    'queryCorrection': {
        'enabled': False,
        'options': {
            'automaticallyCorrect': 'whenNoResults',
        },
    },
    'enableDidYouMean': True,
    'facets': [
        {
            'filterFacetCount': True,
            'injectionDepth': 1000,
            'numberOfValues': 8,
            'sortCriteria': 'alphanumeric',
            'resultsMustMatch': 'atLeastOneValue',
            'type': 'specific',
            'currentValues': [],
            'freezeCurrentValues': False,
            'isFieldExpanded': False,
            'preventAutoSelect': False,
            'facetId': 'amd_press_category',
            'field': 'amd_press_category',
        },
        {
            'filterFacetCount': True,
            'injectionDepth': 1000,
            'numberOfValues': 5,
            'sortCriteria': 'descending',
            'rangeAlgorithm': 'even',
            'resultsMustMatch': 'atLeastOneValue',
            'currentValues': [
                {
                    'start': '2025/06/01@00:07:17',
                    'end': '2025/06/02@00:07:17',
                    'endInclusive': False,
                    'state': 'idle',
                },
                {
                    'start': '2025/05/26@00:07:17',
                    'end': '2025/06/02@00:07:17',
                    'endInclusive': False,
                    'state': 'idle',
                },
                {
                    'start': '2025/05/02@00:07:17',
                    'end': '2025/06/02@00:07:17',
                    'endInclusive': False,
                    'state': 'idle',
                },
                {
                    'start': '2025/03/02@00:07:17',
                    'end': '2025/06/02@00:07:17',
                    'endInclusive': False,
                    'state': 'idle',
                },
                {
                    'start': '2024/06/02@00:07:17',
                    'end': '2025/06/02@00:07:17',
                    'endInclusive': False,
                    'state': 'idle',
                },
            ],
            'preventAutoSelect': False,
            'type': 'dateRange',
            'facetId': 'amd_release_date',
            'field': 'amd_release_date',
            'generateAutomaticRanges': False,
        },
        {
            'filterFacetCount': True,
            'injectionDepth': 1000,
            'numberOfValues': 1,
            'sortCriteria': 'ascending',
            'rangeAlgorithm': 'even',
            'resultsMustMatch': 'atLeastOneValue',
            'currentValues': [],
            'preventAutoSelect': False,
            'type': 'dateRange',
            'facetId': 'amd_release_date_input_range',
            'generateAutomaticRanges': True,
            'field': 'amd_release_date',
        },
        {
            'filterFacetCount': True,
            'injectionDepth': 1000,
            'numberOfValues': 0,
            'sortCriteria': 'ascending',
            'rangeAlgorithm': 'even',
            'resultsMustMatch': 'atLeastOneValue',
            'currentValues': [],
            'preventAutoSelect': False,
            'type': 'dateRange',
            'facetId': 'amd_release_date_input',
            'field': 'amd_release_date',
            'generateAutomaticRanges': False,
        },
    ],
    'numberOfResults': 12,
    'firstResult': 0,
    'facetOptions': {
        'freezeFacetOrder': False,
    },
}

class AmdSpider(scrapy.Spider):
    name = "amd"
    allowed_domains = ["www.amd.com", "xilinxcomprode2rjoqok.org.coveo.com"]
    
    # API endpoint instead of HTML page
    api_url = "https://xilinxcomprode2rjoqok.org.coveo.com/rest/search/v2"
    base_url = "https://www.amd.com{}"

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer xx5ee91b6a-e227-4c6f-83f2-f2120ca3509e',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.amd.com',
        'priority': 'u=1, i',
        'referer': 'https://www.amd.com/',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    }
    json_data = json_data


    async def start(self):
        number_of_results = 12
        current_page = 1
        json_data['firstResult'] = (current_page - 1) * number_of_results
        current_page += 1
        json_data['numberOfResults'] = number_of_results
        
        yield scrapy.Request(
            url=self.api_url,
            method='POST',
            headers=self.headers,
            callback=self.parse_api,
            body=json.dumps(json_data),
        )

        for current_page in range(2, 3):
            json_data['firstResult'] = (current_page - 1) * number_of_results
            yield scrapy.Request(
                url=self.api_url,
                method='POST',
                headers=self.headers,
                callback=self.parse_api,
                body=json.dumps(json_data),
            )

        


    def parse_api(self, response):
        # inspect_response(response, self)
        articles = response.json()['results']
        for article in articles:
            title = article['title'].strip()
            url = article['clickUri']
            # example: 1747848221000
            date = datetime.fromtimestamp(int(article['raw']['date']) / 1000)
            article_header = self.headers.copy()
            article_header['referer'] = 'https://www.amd.com/en/newsroom/press-release-search.html'
            yield scrapy.Request(
                url=url,
                method='GET',
                callback=self.parse_article,
                headers=article_header,
                meta={
                    'title': title,
                    'url': url,
                    'date': date,
                }
            )

    def parse_article(self, response):
        content: list[str] = response.css( "div.article-container div.text ::text").getall()
        content = [c.strip() for c in content if c.strip()]
        content = '\n'.join(content)

        yield {
            'spider': self.name,
            'title': response.meta['title'],
            'url': response.meta['url'],
            'date': response.meta['date'],
            'content': content,
        }
