from lxml import html
import requests

url = 'https://free-proxy-list.net/'
document = html.fromstring(requests.get(url).text)

PROXIES = []

for row in document.xpath("//table[@id='proxylisttable']//tr"):
    if len(row.xpath('./td[1]/text()')) > 0 and len(row.xpath('./td[2]/text()')) > 0:
        if 'yes' in row.xpath('./td[7]/text()')[0]:
            PROXIES.append('https://' + row.xpath('./td[1]/text()')[0] + ':' + row.xpath('./td[2]/text()')[0])
        else:
            PROXIES.append('http://' + row.xpath('./td[1]/text()')[0] + ':' + row.xpath('./td[2]/text()')[0])
PROXIES = list(set(PROXIES))
