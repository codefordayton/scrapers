__author__ = 'dwcaraway'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse
import re
import lxml
import datetime
from dayton.items import DaytonlocalItem
import phonenumbers

facebook_matcher = re.compile('.*GoHere=(.*facebook.*)')
twitter_matcher = re.compile('.*GoHere=(.*twitter.*)')
category_matcher = re.compile('.*[.]com/(.*)[.]asp')

class DaytonLocalSpider(Spider):
    name = "dayton_local"
    allowed_domains = ["daytonlocal.com"]
    start_urls = [
        "http://www.daytonlocal.com/directory.asp"
    ]

    def parse(self, response):
        sel = Selector(response)
        links = sel.css('#MainContentArea div.clearc a').xpath('@href').extract()
        return [Request(url=link, callback=self.paginate) for link in links if not link.startswith('#')]

    def paginate(self, response):
        sel = Selector(response)
        links = sel.xpath("//div[contains(@class,'dright')]/a/ @href").extract()
        link_req_objs = [Request(url=link, callback=self.extract) for link in links]
        next_url = sel.xpath("//a[text()='Next']/@href").extract()
        if next_url:
            link_req_objs.append(Request(url=urlparse.urljoin(response.url, next_url[0]), callback=self.paginate))

        return link_req_objs


    def extract(self, response):
        """
        Takes the data out of the pages at www.daytonlocal.com/listings/*
        """

        sel = Selector(response)

        logo = sel.xpath('//*[@id="MainContentArea"]//div[contains(@class, "dright")]/a/img/ @src').extract()

        item = DaytonlocalItem()

        items = []

        for card in sel.xpath('//div[contains(@class, "vcard")]'):

            item['data_source_url'] = response.url
            item['retrieved_on'] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

            name = card.xpath('//*[contains(@class, "fn")]//strong/text()').extract()
            item['name'] = name[0] if name else None

            website = card.xpath('//*[contains(@class, "fn")]//a/ @href').extract()
            item['website'] = website[0] if website else None

            item['logo'] = urlparse.urljoin('http://www.daytonlocal.com', logo[0]) if logo else None

            address1 = card.xpath('//span[contains(@class, "street-address")]/text()').extract()
            item['address1'] = address1[0] if address1 else None

            # This ones weird..the text we want is between two <br> tags
            addr_div = card.css('.adr').extract()
            address2 = None
            if addr_div:
                br = lxml.html.fromstring(addr_div[0]).cssselect('br')
                if br:
                    address2 = br[0].tail
            item['address2'] = address2

            city = card.xpath('//span[contains(@class, "locality")]/text()').extract()
            item['city'] = city[0] if city else None

            state = card.xpath('//span[contains(@class, "region")]/text()').extract()
            item['state'] = state[0] if state else None

            zipcode = card.xpath('//span[contains(@class, "postal-code")]/text()').extract()
            item['zip'] = zipcode[0] if zipcode else None

            special_divs = card.xpath('div[contains(@class, "clearl")]')

            if special_divs:
                phone = special_divs[0].xpath('text()').extract()
                try:
                    p = phonenumbers.parse(phone[0], 'US')
                    p = phonenumbers.normalize_digits_only(p)
                    item['phone'] = p
                except Exception as e:
                    item['phone'] = None
                    print(e)

            if len(special_divs) >=3:
                descr = special_divs[2].xpath('text()').extract()
                item['description'] = descr[0] if descr else None

            item['facebook'] = None
            item['twitter'] = None
            item['category'] = None

            #social media links
            hrefs = special_divs[1].xpath('a/ @href').extract()
            for href in hrefs:
                if 'facebook' in href:
                    item['facebook'] = facebook_matcher.match(href).group(1)
                elif 'twitter' in href:
                    item['twitter'] = twitter_matcher.match(href).group(1)
                else:
                    match = category_matcher.match(href)
                    if match:
                        item['category'] = match.group(1).split('/')

            #Strip all strings
            for k, v in item.iteritems():
                if isinstance(v, basestring):
                    item[k] = v.strip()

            items.append(item)

        return items


if __name__ == '__main__':
    #Run data extraction test on individual page
    urls = ['http://www.daytonlocal.com/listings/gounaris-denslow-abboud.asp',
            'http://www.daytonlocal.com/listings/indian-ripple-dental.asp']
    import requests
    from scrapy.http import Request, HtmlResponse

    for url in urls:
        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=requests.get(url).text, encoding='utf-8')

        print(DaytonLocalSpider.extract(DaytonLocalSpider(), response=response))

