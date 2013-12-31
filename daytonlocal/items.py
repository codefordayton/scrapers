# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class DaytonlocalItem(Item):
    # define the fields for your item here like:
    # name = Field()
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
