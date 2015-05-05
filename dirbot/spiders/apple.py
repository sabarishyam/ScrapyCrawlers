import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field

class Apple(Item):

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

    #Couldnot find the following commented fields in the webpage

    #store_email = Field()
    #store_floor_plan_url = Field()    
    #store_id = Field()
    #weekly_ad_url = Field()

    zipcode = Field()

class AppleSpider(CrawlSpider):
    name = "apple"
    allowed_domains = ["apple.com"]
    rules = (Rule(LxmlLinkExtractor(allow=(r'(/[a-z]{2})?/retail/[a-z]+/')), callback='parse_obj', follow='True'),)
    start_urls = [
        "http://www.apple.com/retail/storelist/"
    ]

    def parse_obj(self, response):

        sel = Selector(response)

        items = Apple()

        try:
            #City
            items['city']  = sel.xpath('//span[@class="locality"]/text()').extract()[0]

            #Address
            items['address'] = sel.xpath('//div[@class="street-address"]/text()').extract()[0]

            #Store-Country
            store_country = urlparse.urlsplit(response.url).path.split('retail')
            if not store_country[0]:
                items['store_country'] = 'us'
            else:
                items['store_country'] = store_country[0][1:-1]

            #Store Hours
            items['store_hours'] = {}
            store_hours = sel.xpath('//table[@class="store-info"]//tr//td').extract()[1:]
            day_of_week = store_hours[::2]
            day_hours = store_hours[1::2]

            # Need to revisit sanitizing strings of  : , <html_tags> 
            for day in day_of_week:

                index = day_of_week.index(day)
                day = day.replace('<td>','').replace('</td>','')
                day_hours[index] = day_hours[index].replace('<td>','').replace('</td>','')
                items['store_hours'][day] = day_hours[index].strip()

            #Store Services
            items['store_services'] = sel.xpath('//div[@class="nav-buttons selfclear"]//a//@href').extract()
            
            #Store Image Url
            items['store_image_url'] = sel.xpath('//div[@class="column last"]//img//@src').extract()[0]

            #Store Url
            items['store_url'] = response.url

            #Store Name
            items['store_name'] = sel.xpath('//div[@class="store-name"]/text()').extract()[0]

            #Store Phone Number
            items['phone'] = sel.xpath('//div[@class="telephone-number"]/text()').extract()[0]

            #Store State
            items['state'] = sel.xpath('//span[@class="region"]/text()').extract()[0]

            #Store Zipcode
            items['zipcode'] = sel.xpath('//span[@class="postal-code"]/text()').extract()[0]

        except Exception,e:
            pass

        return items
