# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class PickupPoint():
  name = Field()
  contact = Field()
  phone = Field()
  address1 = Field()
  address2 = Field()
  city = Field()
  state = Field()
  zip = Field()
  note = Field()

class LocalharvestItem(Item):
  name = Field()
  description = Field()
  pickups = Field()
  season = Field()
  csa_type = Field()
  since = Field()
  share_quantity = Field()
  full_share_cost = Field()
  half_share_cost = Field()
  work_required = Field()
  farming_practices = Field()
  website = Field()
  data_source_url = Field()
  retrieved_on = Field()
