import datetime
import urllib.request
import zipfile
import glob
import csv
import re
import os
import scrapy
from scrapy.selector import Selector
from dayton.items import ReapItem
from scrapy.shell import inspect_response

this_year = None
extended_year = False

BASE = "//*[@class='main-wrap clearfix']/div[@class='entry col-md-9']/article[@class='post clearfix']"  # noqa
TAX_ELIGIBLE = BASE + "/table[2]/tr/td/table[3]/tr[2]/td[1]/text()"
TAX_ELIGIBLE_2 = BASE + "/table[2]/tr/td/table[3]/tr[2]/td[2]/text()"
PAYMENT_PLAN = BASE + "/div/form/div[1]/tr/td/font/text()"
AMOUNT_DUE = BASE + "/div/form/table[4]/tr[last()]/td[last()]/b/text()"
URL = "https://www.mcohio.org/government/elected_officials/treasurer/mctreas/master.cfm?parid={0}&taxyr={1}&own1={2}"


def fiscal_year():
    today = datetime.datetime.now()
    global this_year
    global extended_year
    if this_year is None and today.month >= 10:
        this_year = today.year
        extended_year = True
    elif this_year is None:
        this_year = today.year - 1
    return this_year


def year_in_range(year):
    if extended_year:
        return year == fiscal_year() - 2 or year == fiscal_year() - 3
    else:
        return year == fiscal_year() - 1 or year == fiscal_year() - 2


def single(array):
    return len(array) == 1


def zero(array):
    return "$0.00" in array[0]


def single_zero(array):
    return single(array) and zero(array)


def real(array):
    return "Real" in array[0]


def single_real(array):
    return single(array) and real(array)


def get_val_year(row):
    return row.xpath('td[1]/text()').extract()


def get_val_type(row):
    return row.xpath('td[2]/b/text()').extract()


def get_val_paid(row):
    return row.xpath('td[5]/text()').extract()


def get_val_due(row):
    return row.xpath('td[6]/text()').extract()


def is_zero_due(sel):
    return single_zero(
        sel.xpath(AMOUNT_DUE).extract())


class ReapSpider(scrapy.Spider):
    name = 'reap'
    fiscal_year()
    allowed_domains = ['mctreas.org', 'mcohio.org']
    start_urls = [
        'http://www.mctreas.org/mctreas/fdpopup.cfm?dtype=DQ'
    ]

    def parse(self, response):
        delinquent_link = Selector(response).xpath(
            '//*[@id="box1"]/td[1]/li/font/i/a/@href').extract()
        urllib.request.urlretrieve(response.urljoin(delinquent_link[0]),
                                   'delinquent.zip')
        unzip('delinquent.zip', 'delinquent')

        with open(glob.glob('delinquent/*.csv')[0], 'rt') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            headers = next(csvreader)
            for idx, column in enumerate(headers):
                column = re.sub('["]', "", column).strip()
                if column.startswith("PARCELID"):
                    parcelidcol = idx
                if column.startswith("OWNERNAME1"):
                    ownernamecol = idx
                if column.startswith("PARCELLOCATION"):
                    parcellocationcol = idx
                if column.startswith("CLS"):
                    parcelclass = idx
                if column.startswith("ASMTBLDG"):
                    buildingvalue = idx
            for row in csvreader:
                if (len(row) > ownernamecol):
                    item = ReapItem()
                    item['parcel_id'] = re.sub('["]', "", row[parcelidcol]).strip()
                    item['parcel_location'] = row[parcellocationcol].strip()
                    item['parcel_class'] = row[parcelclass].strip()
                    item['building_value'] = row[buildingvalue].strip()
                    request = scrapy.Request(URL.format(
                            item['parcel_id'],
                            str(fiscal_year()),
                            row[ownernamecol]),
                        callback=self.get_tax_eligibility)
                    request.meta['item'] = item
                    yield request

    def get_tax_eligibility(self, response):
        sel = Selector(response)

        item = response.meta['item']
        item['tax_eligible'] = re.sub(
            '&nbsp', '', sel.xpath(TAX_ELIGIBLE).extract()[0]).strip()
        if item['tax_eligible'] == 'Eligible':
            item['tax_eligible'] = re.sub(
                '&nbsp', '', sel.xpath(TAX_ELIGIBLE_2).extract()[0]).strip()
        request = scrapy.Request(response.url.replace('master.cfm',
                                                      'taxes.cfm'),
                                 callback=self.get_payment_plan)
        request.meta['item'] = item

        return request

    def get_payment_plan(self, response):
        sel = Selector(response)
        item = response.meta['item']
        item['payment_plan'] = False
        item['payment_window'] = False
        item['lastYear'] = fiscal_year()

        for paymentplan in sel.xpath(PAYMENT_PLAN).extract():
            pp = 'Delinquent Contract' in paymentplan or item['payment_plan']
            item['payment_plan'] = pp
        first_year = None
        rows = sel.xpath('//form/table[4]')

        if is_zero_due(sel):
            item['payment_window'] = True
        else:
            for row in rows.xpath('tr'):
                val_year = get_val_year(row)
                if single(val_year):
                    year = int(val_year[0])
                else:
                    continue
                if first_year is None:
                    item['lastYear'] = year - 1
                    first_year = year - 1

                val_type = get_val_type(row)
                if single_real(val_type):
                    val_paid = get_val_paid(row)
                    val_due = get_val_due(row)
                    # Rules:
                    # Last two full tax years have no payments
                    if year_in_range(year) and (
                            (single(val_paid) and not zero(val_paid)) or (single_zero(val_due))):
                        item['payment_window'] = True
                    if single(val_paid) and not zero(val_paid) and single_zero(val_due):
                        item['lastYear'] = year
                    elif single(val_paid) and not zero(val_paid):
                        item['lastYear'] = year - 1
                else:
                    continue

        reapitems = csv.writer(open('reapitems.csv', 'a'),
                               delimiter=',', quoting=csv.QUOTE_MINIMAL)
        reapitems.writerow([
            item['parcel_id'],
            item['parcel_location'],
            item['tax_eligible'],
            item['payment_plan'],
            item['lastYear'],
            item['payment_window'],
            item['parcel_class'],
            item['building_value']])


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
