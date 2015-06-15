import scrapy
from scrapy.http import FormRequest
from scrapy.selector import Selector
from dayton.items import ReapItem
import urllib
from urllib2 import urlparse
from decimal import Decimal
import zipfile
import glob
import csv
import re
from datetime import datetime

class ReapSpider(scrapy.Spider):
    name = 'reap'
    allowed_domains = ['mctreas.org','mcohio.org']
    start_urls = [
        'http://www.mcohio.org/mctreas/fdpopup.cfm?dtype=DQ'
    ]

    def parse(self, response):
        
        delinquentLink = Selector(response).xpath('//*[@id="box1"]/td[1]/li/font/i/a/@href').extract()
        urllib.urlretrieve (urlparse.urljoin(response.url, delinquentLink[0]), 'delinquent.zip')
        unzip('delinquent.zip', 'delinquent')

        with open (glob.glob('delinquent/*.csv')[0], 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for idx, column in enumerate(csvreader.next()):
                column = re.sub('["]', "", column).strip()
                if column.startswith("PARCELID"):
                    parcelidcol = idx
                if column.startswith("OWNERNAME1"):
                    ownernamecol = idx
                if column.startswith("PARCELLOCATION"):
                    parcellocationcol = idx
            for row in csvreader:
                item = ReapItem()
                item['parcel_id'] = re.sub('["]', "", row[parcelidcol]).strip()
                item['parcel_location'] = row[parcellocationcol].strip()
                if item['parcel_id'].startswith('R72'):
                    request = scrapy.Request("http://mctreas.org/master.cfm?parid=" + item['parcel_id'] + "&taxyr=2014" + "&own1=" + row[ownernamecol] + '\n', callback=self.getTaxEligibility)
                    request.meta['item'] = item
                    yield request

    def getTaxEligibility(self, response):
        sel = Selector(response)

        item = response.meta['item']
        item['tax_eligible'] = re.sub('&nbsp', '', sel.xpath('//*[@id="content_middle_wide"]/table[2]/tr/td/table[3]/tr[2]/td[1]/text()').extract()[0]).strip()
        if item['tax_eligible'] == 'Eligible':
            item['tax_eligible'] = re.sub('&nbsp', '', sel.xpath('//*[@id="content_middle_wide"]/table[2]/tr/td/table[3]/tr[2]/td[2]/text()').extract()[0]).strip()
        request = scrapy.Request(response.url.replace('master.cfm', 'pymtsbusdate.cfm'), callback=self.getPaymentPlan)
        request.meta['item'] = item

        return request

    def getPaymentPlan(self, response):
        sel = Selector(response)
        item = response.meta['item']
        item['payment_plan'] = False
        
        for paymentXPath in sel.xpath('//*[@id="content_middle_wide"]/div[3]/form/table/tr'):
            data = paymentXPath.xpath('./td/text()').extract()
            # if not an empty list, nor different size than 2, since the date might be omitted
            if data and len(data) == 2:
                date = datetime.strptime(data[0].strip(), '%m-%d-%Y')
                payment =  Decimal(re.sub(r'[^\d.]', '', data[1]))
                if date.year > datetime.today().year - 3 and payment > 0:
                    item['payment_plan'] = True
        reapitems = csv.writer(open('reapitems.csv', 'ab'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
        reapitems.writerow([item['parcel_id'], item['parcel_location'], item['tax_eligible'], item['payment_plan']])

# shamelessly copied from a stack overflow post
def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)
