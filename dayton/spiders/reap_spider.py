import urllib
from urllib2 import urlparse
import zipfile
import glob
import csv
import re
import os
import scrapy
from scrapy.selector import Selector
from dayton.items import ReapItem
#from scrapy.shell import inspect_response

YEAR = 2016
BASE_XPATH = "//*[@class='main-wrap clearfix']/div[@class='entry col-md-9']/article[@class='post clearfix']"
TAX_ELIGIBLE_XPATH = BASE_XPATH + "/table[2]/tr/td/table[3]/tr[2]/td[1]/text()"
TAX_ELIGIBLE_XPATH2 = BASE_XPATH + "/table[2]/tr/td/table[3]/tr[2]/td[2]/text()"
PAYMENT_PLAN_XPATH = BASE_XPATH + "/div/form/div[1]/tr/td/font/font/b/text()"

def year_in_range(year):
    return year == YEAR - 2 or year == YEAR - 3

def single(array):
    return len(array) == 1

def zero(array):
    return "$0.00" in array[0]

class ReapSpider(scrapy.Spider):
    name = 'reap'
    allowed_domains = ['mctreas.org', 'mcohio.org']
    start_urls = [
        'http://www.mctreas.org/fdpopup.cfm?dtype=DQ'
    ]

    def parse(self, response):
        delinquent_link = Selector(response).xpath(
            '//*[@id="box1"]/td[1]/li/font/i/a/@href').extract()
        urllib.urlretrieve(urlparse.urljoin(response.url, delinquent_link[0]), 'delinquent.zip')
        unzip('delinquent.zip', 'delinquent')

        with open(glob.glob('delinquent/*.csv')[0], 'rb') as csvfile:
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
                    request = scrapy.Request(
                        "http://mctreas.org/master.cfm?parid={0}&taxyr={1}&own1={2}".format(
                            item['parcel_id'], str(YEAR - 1), row[ownernamecol]),
                        callback=self.get_tax_eligibility)
                    request.meta['item'] = item
                    yield request

    def get_tax_eligibility(self, response):
        sel = Selector(response)

        item = response.meta['item']
        item['tax_eligible'] = re.sub(
            '&nbsp', '', sel.xpath(TAX_ELIGIBLE_XPATH).extract()[0]).strip()
        if item['tax_eligible'] == 'Eligible':
            item['tax_eligible'] = re.sub(
                '&nbsp', '', sel.xpath(TAX_ELIGIBLE_XPATH2).extract()[0]).strip()
        request = scrapy.Request(response.url.replace('master.cfm', 'taxes.cfm'),
                                 callback=self.get_payment_plan)
        request.meta['item'] = item

        return request

    def get_payment_plan(self, response):
        sel = Selector(response)
        item = response.meta['item']
        item['payment_plan'] = False
        item['payment_window'] = False
        for paymentplan in sel.xpath(PAYMENT_PLAN_XPATH).extract():
            item['payment_plan'] = 'Unapplied Payments:' in paymentplan or item['payment_plan']
        first_year = None
        item['lastYear'] = YEAR
        rows = sel.xpath('//form/table[4]')
        for row in rows.xpath('tr'):
            val = row.xpath('td[1]/text()').extract()
            if single(val):
                year = int(val[0])
            else:
                continue
            if first_year is None:
                item['lastYear'] = year - 1
                first_year = year - 1
            # Data points
            # td[2]/text() is 'Real/Project' - 'real' represents tax data that we care about
            # td[5]/text() is 'Payments' - how we tell if a payment was made
            val_type = row.xpath('td[2]/b/text()').extract()
            val = row.xpath('td[5]/text()').extract()
            val_due = row.xpath('td[6]/text()').extract()
            if single(val_type) and val_type[0] == u'Real\xa0':
                # Rules:
                # Last two full tax years have no payments
                if year_in_range(year) and (
                        (single(val) and not zero(val)) or (single(val_due) and zero(val_due))):
                    item['payment_window'] = True
                if single(val) and not zero(val) and single(val_due) and zero(val_due):
                    item['lastYear'] = year
                elif single(val) and not zero(val):
                    item['lastYear'] = year - 1
            else:
                continue

        reapitems = csv.writer(open('reapitems.csv', 'ab'),
                               delimiter=',', quoting=csv.QUOTE_MINIMAL)
        reapitems.writerow([
            item['parcel_id'],
            item['parcel_location'],
            item['tax_eligible'],
            item['payment_plan'],
            item['lastYear'],
            item['payment_window']])

def unzip(source_filename, dest_dir):
    """
    shamelessly copied from a stack overflow post
    """
    with zipfile.ZipFile(source_filename) as zipf:
        for member in zipf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zipf.extract(member, path)
