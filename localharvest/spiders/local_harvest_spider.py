__author__ = 'davidebest'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse
import re
import lxml
import datetime
import sys
sys.path.append('/vagrant/localharvest')

from items import LocalharvestItem, PickupPoint
import phonenumbers

class LocalHarvestSpider(Spider):
    name = "CodeForDayton"
    allowed_domains = ["localharvest.org"]
    start_urls = [
        "http://www.localharvest.org/search.jsp?jmp&scale=9&lat=39.758948&lon=-84.191607&ty=6"
    ]

    def parse(self, response):
        sel = Selector(response)
        links = sel.css('#content h4.inline a').xpath('@href').extract()
        link_req_objs = [Request(url="http://www.localharvest.org" + link, callback=self.extract) for link in links]
        print link_req_objs
        return link_req_objs

    def paginate(self, response):
        sel = Selector(response)
        links = sel.css('#content div.pagination a').xpath('@href').extract()
        link_req_objs = [Request(url=link, callback=self.extract) for link in links]
        next_url = sel.xpath("//a[text()='>>']/@href").extract()
        if next_url:
            link_req_objs.append(Request(url=urlparse.urljoin(response.url, next_url[0]), callback=self.paginate))

        return link_req_objs


    def extract(self, response):
        """
        Takes the data out of the pages at http://www.localharvest.org/csa/*
        """

        sel = Selector(response)

        pickupPoints = []
        item = LocalharvestItem()
        pickupPoint = PickupPoint()

        item['name'] = sel.css('#listingbody h1 a').xpath('text()').extract()[0]
        item['description'] = sel.css('.textBlock p').xpath('text()').extract()[0]

        pickups = sel.xpath('//h4[text()="Pick Up / Drop Off Points"]/following-sibling::*').extract()
        for pickup in pickups:
          if len(pickup) > 5 and pickup.find('dottedline') == -1:
            #Title Line
            if pickup.find('img') > 0:
              # Get title
              mobj = re.search('<b>(.*?)</b>', pickup)
              if mobj:
                pickupPoint.name = mobj.groups()[0]
              # Get days
              mobj = re.search('\((.*)\)</span>', pickup)
              if mobj:
                pickupPoint.days = mobj.groups()[0]
              # Get Description
              mobj = re.search('<br>\s*(.*)\s*</p>', pickup)
              if mobj:
                pickupPoint.description = mobj.groups()[0]
            elif pickup.find('Contact') > 0:
              # Get Contact
              mobj = re.search('</b>\s*(.*?)<br>', pickup)
              if mobj:
                pickupPoint.contact = mobj.groups()[0]
              # Get phone
              mobj = re.search('Phone:</b>\s*(.*?)<br>', pickup)
              if mobj:
                pickupPoint.phone = mobj.groups()[0]
              # Get address
              mobj = re.search('Address:</b><br>\s*(.*?)<br>', pickup)
              if mobj:
                pickupPoint.address1 = mobj.groups()[0]
              # Get City, State, Zip
              mobj = re.search('<br>\s*(.*),\s(.*)\s(.*)', pickup)
              if mobj:
                pickupPoint.city = mobj.groups()[0]
                pickupPoint.state = mobj.groups()[1]
                pickupPoint.zip = mobj.groups()[2]
            elif pickup.find('Address') > 0:
              mobj = re.search('Address:</b><br>\s*(.*?)<br>', pickup)
              if mobj:
                pickupPoint.address = mobj.groups()[0]
              # Get City, State, Zip
              mobj = re.search('<br>\s*(.*),\s(.*)\s(.*)', pickup)
              if mobj:
                pickupPoint.city = mobj.groups()[0]
                pickupPoint.state = mobj.groups()[1]
                pickupPoint.zip = mobj.groups()[2]
          elif pickup.find('dottedline') > 0:
            pickupPoints.append(pickupPoint)
            pickupPoint = PickupPoint()

        item['pickups'] = pickupPoints
        return item


if __name__ == '__main__':
    #Run data extraction test on individual page
    urls = ['http://www.localharvest.org/csa/M18016', 'http://www.localharvest.org/csa/M61994']
    import requests
    from scrapy.http import Request, HtmlResponse

    for url in urls:
        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=requests.get(url).text, encoding='utf-8')

        print LocalHarvestSpider.extract(LocalHarvestSpider(), response=response)
