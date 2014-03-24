__author__ = 'dwcaraway'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import FormRequest
import datetime
from dayton.items import DaytonChamberItem
import phonenumbers


class DaytonChamberSpider(Spider):
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

        containers = sel.xpath('//div[@id="membersearchresults"]//div[@id="container"]')

        for container in containers:

            item = DaytonChamberItem()

            item['data_source_url'] = response.url
            item['retrieved_on'] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

            rows = container.css('div.row')

            row_dict = {}
            key = value = None

            for row in rows:
                try:
                    key = row.css('div.leftcol').xpath('./text()').extract()[0].strip()

                    try:
                        value = row.css('div.rightcol').xpath('./text()').extract()[0].strip()
                    except IndexError:
                        value = row.css('div.rightcol').xpath('./text()').extract()[0].strip()

                        pass

                except IndexError:
                    pass




            item['name'] = rows[1].xpath('./strong/text()').extract()[0].strip()
            item['category'] = rows[3].xpath('./text()').extract()[0].strip()
            item['contact_name'] = rows[4].xpath('./text()').extract()[0].strip()
            item['contact_title'] = rows[5].xpath('./text()').extract()[0].strip()
            item['address']= rows[6].xpath('./text()').extract()[0].strip()

            #Normalize phone numbers
            try:
                p_original = rows[7].xpath('./text()').extract()[0].strip()
                p = phonenumbers.parse(p_original, 'US')
                p = phonenumbers.normalize_digits_only(p)
                item['phone'] = p
            except Exception:
                #Non-standard phone, so just going to store the original
                item['phone'] = p_original

            #TODO remove
            from scrapy.shell import inspect_response
            inspect_response(response)

            item['website'] = rows[9].xpath('./a/ @href').extract()[0].strip()

            items.append(item)

            #TODO remove
            self.log("item: %s" % item)

        return items

if __name__ == '__main__':
    from scrapy.http import Request
    from scrapy.http.response.xml import XmlResponse


    with open('./text.html', 'r') as f:
        request = Request(url='http://localhost')
        response = XmlResponse(url='http://localhost', request=request, body=f.read(), encoding='utf-8')

    print DaytonChamberSpider.extract(DaytonChamberSpider(), response=response)
