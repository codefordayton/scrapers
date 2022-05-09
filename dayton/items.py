# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.item import Item, Field


class ReapItem(scrapy.Item):
    parcel_id = scrapy.Field()
    parcel_location = scrapy.Field()
    tax_eligible = scrapy.Field()
    payment_plan = scrapy.Field()
    date_eligible = scrapy.Field()
    payment_window = scrapy.Field()
    lastYear = scrapy.Field()
    parcel_class = scrapy.Field()
    building_value = scrapy.Field()
