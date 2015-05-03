import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field

class Hhgreg(Item):

    city = Field()
    address = Field()
    store_country = Field()
    store_services = Field()
    store_hours = Field()
    store_image_url = Field()
    store_name = Field()
    store_url = Field()
    phone = Field()
    state = Field()
    #store_email = Field()
    #store_floor_plan_url = Field()
    #store_id = Field()
    #weekly_ad_url = Field()
    zipcode = Field()

class HhgregSpider():
    