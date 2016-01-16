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
#from scrapy.shell import inspect_response

YEAR = 2016

def yearInRange(year):
    return (year == YEAR - 2 or year == YEAR - 3)

def single(array):
    return len(array) == 1

def zero(array):
    return "$0.00" in array[0]

class ReapSpider(scrapy.Spider):
    name = 'reap'
    allowed_domains = ['mctreas.org','mcohio.org']
    start_urls = [
        'http://www.mctreas.org/fdpopup.cfm?dtype=DQ'
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
                    request = scrapy.Request("http://mctreas.org/master.cfm?parid=" + item['parcel_id'] + "&taxyr=" + str(YEAR - 1) + "&own1=" + row[ownernamecol] + '\n', callback=self.getTaxEligibility)
                    request.meta['item'] = item
                    yield request

    def getTaxEligibility(self, response):
        sel = Selector(response)

        item = response.meta['item']
        item['tax_eligible'] = re.sub('&nbsp', '', sel.xpath("//*[@class='main-wrap clearfix']/div[@class='entry col-md-9']/article[@class='post clearfix']/table[2]/tr/td/table[3]/tr[2]/td[1]/text()").extract()[0]).strip()
        if item['tax_eligible'] == 'Eligible':
            item['tax_eligible'] = re.sub('&nbsp', '', sel.xpath("//*[@class='main-wrap clearfix']/div[@class='entry col-md-9']/article[@class='post clearfix']/table[2]/tr/td/table[3]/tr[2]/td[2]/text()").extract()[0]).strip()
        request = scrapy.Request(response.url.replace('master.cfm', 'taxes.cfm'), callback=self.getPaymentPlan)
        request.meta['item'] = item

        return request

    def getPaymentPlan(self, response):
        sel = Selector(response)
        item = response.meta['item']
        item['payment_plan'] = False
        item['payment_window'] = False
        for paymentplan in sel.xpath("//div[@class='main-wrap clearfix']/div[@class='entry col-md-9']/article[@class='post clearfix']/div/form/div[1]/tr/td/font/font/b/text()").extract():
            item['payment_plan'] = 'Unapplied Payments:' in paymentplan or item['payment_plan']
        firstYear = None
        item['lastYear'] = YEAR 
        rows = sel.xpath('//form/table[4]')
        for tr in rows.xpath('tr'):
            val = tr.xpath('td[1]/text()').extract()
            if single(val):
                year = int(val[0])
            else:
                continue
            if firstYear is None:
                item['lastYear'] = year - 1 
                firstYear = year - 1
            # Data points
            # td[2]/text() is 'Real/Project' - 'real' represents tax data that we care about
            # td[5]/text() is 'Payments' - how we tell if a payment was made
            valType = tr.xpath('td[2]/b/text()').extract()
            val = tr.xpath('td[5]/text()').extract()
            valDue = tr.xpath('td[6]/text()').extract()
            #print('first values', len(valType), valType)
            if single(valType) and valType[0] == u'Real\xa0':
                #print('values', valType[0], thisYear, year, val[0])
                #inspect_response(response, self)
                # Rules:
                # Last two full tax years have no payments
                if yearInRange(year) and ((single(val) and not zero(val)) or (single(valDue) and zero(valDue))):
                    item['payment_window'] = True
                if single(val) and not zero(val) and single(valDue) and zero(valDue):
                    item['lastYear'] = year
                elif single(val) and not zero(val):
                    item['lastYear'] = year - 1
            else:
                continue

        reapitems = csv.writer(open('reapitems.csv', 'ab'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
        reapitems.writerow([item['parcel_id'], item['parcel_location'], item['tax_eligible'], item['payment_plan'], item['lastYear'], item['payment_window']])

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
