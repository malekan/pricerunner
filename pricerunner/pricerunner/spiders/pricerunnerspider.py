import traceback
from urllib.parse import urljoin
from pricerunner.items import PricerunnerItem
from lxml import html
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import requests
from scrapy import Request
from pricerunner.proxies import PROXIES
import random

class PricerunnerSpider(CrawlSpider):
    name = shop_name = 'pricerunner.com'
    allowed_domains = [shop_name]
    main_category_urls = ['https://www.pricerunner.com/t/15/compare-Sound-prices',]
                  # 'https://www.pricerunner.com/t/16/compare-Vision-prices',
                  # 'https://www.pricerunner.com/t/22/compare-Computers-prices',
                  # 'https://www.pricerunner.com/t/4/compare-Phones-prices',
                  # 'https://www.pricerunner.com/t/35/compare-Kids-and-Family-prices',
                  # 'https://www.pricerunner.com/t/3/compare-Home-Appliances-prices']

    product_urls = []

    def __init__(self, max_pages=1, *args, **kwargs):
        super(PricerunnerSpider, self).__init__(*args, **kwargs)
        for main_category_url in self.main_category_urls:
            categories_urls = find_categories_urls(main_category_url)
            for url in categories_urls:
                for i in range(int(max_pages)):
                    self.product_urls.extend(find_products_urls(url % i))

    def start_requests(self):
        for url in self.product_urls:
            yield Request(url=url, callback=self.myParse)

    def myParse(self, response):
        name_xpath = "//h1[@itemprop='name']/text()"
        image_xpath = "//img[@itemprop='image']/@src"
        price_row_xpath = "//div[@id='product-prices']//div[@class='_2c08bmYFgl']"
        item = PricerunnerItem()
        item['name'] = response.xpath(name_xpath).get()
        item['image_url'] = response.xpath(image_xpath).get()
        item['url'] = response.url
        # each key name of one store and value is price of this product in store
        prices = {}
        for row in response.xpath(price_row_xpath):
            store = row.xpath(".//div[@class='_2ZuJzhZmMM']/text()").get()
            store = store.replace(',', '').strip()
            price = row.xpath(".//span[@class='_2dHkm6BskV']/text()").get()
            price = price.replace(',', '').strip()
            prices[store] = price
        item['price_lists'] = prices
        yield item


def find_categories_urls(url):
    base_url = "https://www.pricerunner.com/public/v1/cl/{category_id}/uk/desktop?page=%d&urlName={url_name}&sort=0"
    xpath = """//div[@class='ofuLDdJ4J1']/a/@href"""
    response = download_url(url)
    document = html.fromstring(response.text)
    urls = document.xpath(xpath)
    category_urls_list = []
    for url in urls:
        category_id = url.split('/')[2]
        urlName = url.split('/')[3].split('?')[0]
        other = ''
        for p in url.split('/')[3].split('?')[1:]:
            other += '?' + p
        category_urls_list.append(base_url.format(category_id=category_id, url_name=urlName) + other)
    return list(set(category_urls_list))


def find_products_urls(category_api):
    products_urls = []
    response = download_url(category_api).json()
    products = response['viewData']['category']['products']
    for product in products:
        if 'comparePricesLink' in product and product['comparePricesLink'] != '':
            products_urls.append(urljoin(base='https://www.pricerunner.com', url=product['comparePricesLink']))
    return list(set(products_urls))


def download_url(url):
    # proxies = {'https':'http://127.0.0.1:8118'}
    proxies = {'https': random.choice(PROXIES)}
    USER_AGENT_LIST = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.92 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7(KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0)Gecko/16.0 Firefox/16.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10'
    ]

    headers = {
        'User-Agent': random.choice(USER_AGENT_LIST)
    }
    for i in range(10):
        try:
            response = requests.get(url=url, headers=headers, proxies=proxies, timeout=20)
            if response.status_code == 403:
                proxies = {'https': random.choice(PROXIES)}
                continue
            return response
        except Exception as e:
            # print(traceback.format_exc())
            # print(e)
            # print(proxies)
            proxies = {'https': random.choice(PROXIES)}
            continue
