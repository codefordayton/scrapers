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
        "http://www.localharvest.org/search.jsp?jmp&scale=9&lat=39.758948&lon=-84.191607&ty=6&p=1",
        "http://www.localharvest.org/search.jsp?jmp&scale=9&lat=39.758948&lon=-84.191607&ty=6&p=2"
    ]

    download_delay = 2

    def parse(self, response):
        sel = Selector(response)
        links = sel.css('#content h4.inline a').xpath('@href').extract()
        link_req_objs = [Request(url="http://www.localharvest.org" + link, callback=self.extract) for link in links]
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
        item['description'] = sel.css('.textBlock p').xpath('text()').extract()[0].strip()
        item['data_source_url'] = response.url
        item['website'] = 'www.localharvest.org'
        item['retrieved_on'] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

        # Get the CSA details
        csa_details = sel.xpath("/html[@id='csagroup']/body/div[@id='container']/div[@id='contentwrapper']/div[@id='leftcontentwrapper']/div[@id='content']/div[@id='listingbody']/div[2]/div[@class='panel fullwidth']")

        #season
        xpathVar = csa_details.xpath("//div[@class='fullwidth']/div[@class='col two-thirds']/p/span[@class='inlineblock']/b[text()='Season:']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['season'] = xpathVar.extract()[0]
        #csa_type
        xpathVar = csa_details.xpath("//div[@class='fullwidth']/div[@class='col two-thirds']/p/span[@class='inlineblock']/b[text()='Type:']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['csa_type'] = xpathVar.extract()[0]
        #since
        xpath = csa_details.xpath("//div[@class='col three-fourths']/div[@class='fullwidth']/div[@class='col one-third']/p/span[@class='inlineblock']/b[text()='Since:']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['since'] = xpathVar.extract()[0]
        #share_quantity
        xpathVar = csa_details.xpath("//div[@class='col three-fourths']/div[@class='fullwidth']/div[@class='col one-third']/p/span[@class='inlineblock']/b/nobr[text()='# of shares:']/parent::b/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['share_quantity'] = xpathVar.extract()[0]
        #full_share_cost
        xpathVar = csa_details.xpath("//div[@class='col three-fourths']/p/span[@class='inlineblock']/b[text()='Full Share:']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['full_share_cost'] = xpathVar.extract()[0]
        #half_share_cost
        xpathVar = csa_details.xpath("//div[@class='col three-fourths']/p/span[@class='inlineblock']/b[text()='1/2 Share:']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['half_share_cost'] = xpathVar.extract()[0]
        #work_required
        xpathVar = csa_details.xpath("//div[@class='col three-fourths']/p/span[@class='inlineblock']/b[text()='Work Req?']/parent::span/following-sibling::span/text()")
        if xpathVar:
          item['work_required'] = xpathVar.extract()[0]
        #farming_practices
        xpathVar = csa_details.xpath("//div[@class='col one-fourth']/div/ul/li/a/text()")
        if xpathVar:
          item['farming_practices'] = xpathVar.extract()

        # Get the list of pickup points
        pickups = sel.xpath('//h4[text()="Pick Up / Drop Off Points"]/following-sibling::*').extract()
        for pickup in pickups:
          if len(pickup) > 5 and pickup.find('dottedline') == -1:
            #Title Line
            if pickup.find('img') > 0:
              # Get title
              mobj = re.search('<b>(.*?)</b>', pickup)
              if mobj:
                pickupPoint.name = mobj.groups()[0].strip()
              # Get days
              mobj = re.search('\((.*)\)</span>', pickup)
              if mobj:
                pickupPoint.days = mobj.groups()[0]
              # Get Description
              mobj = re.search('<br>\s*([]^\<\w\>]*)\s*</p>', pickup)
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
              mobj = re.search('Address:</b><br>\s*(.*?)\s*<br>', pickup)
              if mobj:
                pickupPoint.address1 = mobj.groups()[0]
              # Get City, State, Zip
              mobj = re.search('<br>\s*(.*),\s(\w*)\s(\d*)', pickup)
              if mobj:
                pickupPoint.city = mobj.groups()[0]
                pickupPoint.state = mobj.groups()[1]
                pickupPoint.zip = mobj.groups()[2]
            elif pickup.find('Address') > 0:
              mobj = re.search('Address:</b><br>\s*(.*?)\s*<br>', pickup)
              if mobj:
                pickupPoint.address = mobj.groups()[0]
              # Get City, State, Zip
              mobj = re.search('<br>\s*(.*),\s(\w*)\s(\d*)', pickup)
              if mobj:
                pickupPoint.city = mobj.groups()[0]
                pickupPoint.state = mobj.groups()[1]
                pickupPoint.zip = mobj.groups()[2]
          elif pickup.find('dottedline') > 0:
            pickupPoints.append(pickupPoint)
            pickupPoint = PickupPoint()

        item['pickups'] = ([p.__dict__ for p in pickupPoints])
        return item


if __name__ == '__main__':
    #Run data extraction test on individual page
    urls = ['http://www.localharvest.org/csa/M17619', 'http://www.localharvest.org/csa/M61994']
    import requests
    from scrapy.http import Request, HtmlResponse

    for url in urls:
        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=requests.get(url).text, encoding='utf-8')

        print LocalHarvestSpider.extract(LocalHarvestSpider(), response=response)
