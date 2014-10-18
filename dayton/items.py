# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class DaytonlocalItem(Item):
    name = Field()
    website = Field()
    logo = Field()
    address1 = Field()
    address2 = Field()
    city = Field()
    state = Field()
    zip = Field()
    phone = Field()
    description = Field()
    facebook = Field()
    twitter = Field()
    category = Field()
    data_source_url = Field()
    retrieved_on = Field()

class DaytonOhioPDFItem(Item):
    title = Field()
    url = Field()
    author = Field()
    pubDate = Field()

class DaytonChamberItem(Item):
    name = Field()
    website = Field()
    address = Field()
    phone = Field()
    category = Field()
    data_source_url = Field()
    retrieved_on = Field()
    contact_name = Field()
    contact_title = Field()

class ReapItem(scrapy.Item):
    parcelid = scrapy.Field()
    parcellocation = scrapy.Field()
    taxeligible = scrapy.Field()
    paymentplan = scrapy.Field()
