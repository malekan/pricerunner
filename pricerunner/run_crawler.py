from subprocess import call
from datetime import datetime


def main():
    call("scrapy crawl pricerunner.com -a max_pages=1 -o result.json", shell=True)


if __name__ == '__main__':
    main()
