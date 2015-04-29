import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector

from dirbot.items import *


class AppleSpider(CrawlSpider):
    name = "apple"
    allowed_domains = ["apple.com"]
    rules = (Rule(LxmlLinkExtractor(allow=("(/[a-z]{2})?/retail/[a-z]+/")), callback='parse_obj', follow='True'),)
    start_urls = [
        "http://www.apple.com/retail/storelist/"
    ]

    def parse_obj(self, response):

        sel = Selector(response)

        items = Apple()
        #import pdb; pdb.set_trace()
        try:
            items['city']  = sel.xpath('//span[@class="locality"]/text()').extract()[0]
            items['address'] = sel.xpath('//div[@class="street-address"]/text()').extract()[0]

            store_country = urlparse.urlsplit(response.url).path.split('retail')
            if not store_country[0]:
                items['store_country'] = 'us'
            else:
                items['store_country'] = store_country[0][1:-1]

            items['store_hours'] = {}
            store_hours = sel.xpath('//table[@class="store-info"]//tr//td').extract()[1:]
            day_of_week = store_hours[::2]
            day_hours = store_hours[1::2]

            # Need to revisit sanitizing strings of  : , <html_tags> 
            for day in day_of_week:

                index = day_of_week.index(day)
                day = day.replace('<td>','').replace('</td>','')
                day_hours[index] = day_hours[index].replace('<td>','').replace('</td>','')
                items['store_hours'][day] = day_hours[index]

            items['store_services'] = sel.xpath('//div[@class="nav-buttons selfclear"]//a//@href').extract()
            
            items['store_image_url'] = sel.xpath('//div[@class="column last"]//img//@src').extract()[0]
            items['store_url'] = response.url
            items['store_name'] = sel.xpath('//div[@class="store-name"]/text()').extract()[0]

            items['phone'] = sel.xpath('//div[@class="telephone-number"]/text()').extract()[0]

            items['state'] = sel.xpath('//span[@class="region"]/text()').extract()[0]
            items['zipcode'] = sel.xpath('//span[@class="postal-code"]/text()').extract()[0]
            #import pdb; pdb.set_trace()
        except:
            #import pdb; pdb.set_trace()
            pass

        return items
