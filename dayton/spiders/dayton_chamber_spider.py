__author__ = 'dwcaraway'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import FormRequest
from scrapy.contrib.loader import ItemLoader
from scrapy import log
from scrapy.http import Request
import urlparse
import re
import lxml
import datetime
from dayton.items import DaytonChamberItem
import phonenumbers

facebook_matcher = re.compile('.*GoHere=(.*facebook.*)')
twitter_matcher = re.compile('.*GoHere=(.*twitter.*)')
category_matcher = re.compile('.*[.]com/(.*)[.]asp')

class DaytonLocalSpider(Spider):
    name = "dayton_chamber"
    allowed_domains = ["daytonchamber.org"]
    start_urls = [
        "http://www.daytonchamber.org/index.cfm/mb/find-a-member1/"
    ]

    def parse(self, response):
        yield FormRequest.from_response(response,
                                        formname='searchForm',
                                        formdata={},
                                        callback=self.extract)

    def extract(self, response):
        """
        Takes the data out of the members entries
        """

        sel = Selector(response)

        items = []

        containers = sel.select('//div[@id="membersearchresults"]//div[@id="container"]')

        for container in containers:

            item = DaytonChamberItem()

            item['data_source_url'] = response.url
            item['retrieved_on'] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

            rows = container.css('div.row div.rightcol')

            item['name'] = rows[1].xpath('./strong/text()').extract()[0].strip()
            item['category'] = rows[3].xpath('./text()').extract()[0].strip()
            item['contact_name'] = rows[4].xpath('./text()').extract()[0].strip()
            item['contact_title'] = rows[5].xpath('./text()').extract()[0].strip()

            #Extract and split addresses
            address = rows[6].xpath('./text()').extract()[0].strip()

            item['address']

            #Normalize phone numbers
            try:
                p = phonenumbers.parse(rows[7].xpath('./text()').extract()[0].strip(), 'US')
                p = phonenumbers.normalize_digits_only(p)
                item['phone'] = p
            except Exception:
                item['phone'] = None


            item['website'] = rows[9].xpath('./a/ @href').extract()[0].strip()

            #TODO invoking the shell, remove when done debugging
            from scrapy.shell import inspect_response
            inspect_response(response)


            # website = card.xpath('//*[contains(@class, "fn")]//a/ @href').extract()
            # item['website'] = website[0] if website else None
            #
            # item['logo'] = urlparse.urljoin('http://www.daytonlocal.com', logo[0]) if logo else None
            #
            # address1 = card.xpath('//span[contains(@class, "street-address")]/text()').extract()
            # item['address1'] = address1[0] if address1 else None
            #
            # # This ones weird..the text we want is between two <br> tags
            # addr_div = card.css('.adr').extract()
            # address2 = None
            # if addr_div:
            #     br = lxml.html.fromstring(addr_div[0]).cssselect('br')
            #     if br:
            #         address2 = br[0].tail
            # item['address2'] = address2
            #
            # city = card.xpath('//span[contains(@class, "locality")]/text()').extract()
            # item['city'] = city[0] if city else None
            #
            # state = card.xpath('//span[contains(@class, "region")]/text()').extract()
            # item['state'] = state[0] if state else None
            #
            # zipcode = card.xpath('//span[contains(@class, "postal-code")]/text()').extract()
            # item['zip'] = zipcode[0] if zipcode else None
            #
            # special_divs = card.xpath('div[contains(@class, "clearl")]')
            #
            # if special_divs:
            #     phone = special_divs[0].xpath('text()').extract()
            #     try:
            #         p = phonenumbers.parse(phone[0], 'US')
            #         p = phonenumbers.normalize_digits_only(p)
            #         item['phone'] = p
            #     except Exception, e:
            #         item['phone'] = None
            #         print e
            #
            # if len(special_divs) >=3:
            #     descr = special_divs[2].xpath('text()').extract()
            #     item['description'] = descr[0] if descr else None
            #
            # item['facebook'] = None
            # item['twitter'] = None
            # item['category'] = None
            #
            # #social media links
            # hrefs = special_divs[1].xpath('a/ @href').extract()
            # for href in hrefs:
            #     if 'facebook' in href:
            #         item['facebook'] = facebook_matcher.match(href).group(1)
            #     elif 'twitter' in href:
            #         item['twitter'] = twitter_matcher.match(href).group(1)
            #     else:
            #         match = category_matcher.match(href)
            #         if match:
            #             item['category'] = match.group(1).split('/')
            #
            # #Strip all strings
            # for k, v in item.iteritems():
            #     if isinstance(v, basestring):
            #         item[k] = v.strip()
            #
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

        print DaytonLocalSpider.extract(DaytonLocalSpider(), response=response)

