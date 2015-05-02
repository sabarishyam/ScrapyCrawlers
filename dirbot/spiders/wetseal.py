import urlparse
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import FormRequest
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field

regex = re.compile(r'[\n\r\t]')

class Wetseal(Item):

    city = Field()
    address = Field()
    store_country = Field()
    #store_services = Field()
    store_hours = Field()
    #store_image_url = Field()
    store_name = Field()
    #store_url = Field()
    phone = Field()
    state = Field()
    #store_email = Field()
    #store_floor_plan_url = Field()
    store_id = Field()
    #weekly_ad_url = Field()
    zipcode = Field()


class WetsealSpider(Spider):
    name = "wetseal"
    allowed_domains = ["wetseal.com"]
    start_urls = ["http://www.wetseal.com/Stores"]

    def parse(self, response):

        sel = Selector(response)
        form_url = sel.xpath('//form[@id="dwfrm_storelocator_state"]/@action').extract()
        states = sel.xpath('//option[@value]/@value').re(r'[A-Z]+')

        #import pdb;pdb.set_trace()

        for state in states:            
            yield FormRequest(url=''.join(form_url),
                            formdata={'dwfrm_storelocator_address_states_stateUSCA': state,
                                      'dwfrm_storelocator_findbystate': 'Search'},
                            callback=self.parse1)

    def parse1(self, response):

        sel = Selector(response)
        #import pdb;pdb.set_trace()

        #Needs cleansing of html 
        store_address_list =  sel.xpath('//td[@class="store-address"]')
        store_name_list = sel.xpath('//div[@class="store-name"]/text()').extract()
        store_hours_args = sel.xpath('//div[@class="store-hours"]')
        store_state = response.request.body.split('=')[-1]

        items = []

        for address in store_address_list:
            
            item = Wetseal()
            index = store_address_list.index(address)
            _args = address.extract().replace('\t','').split('\n')[1:-1]
            
            store_hours = regex.sub('', store_hours_args[index].extract()).strip('<div class="store-hours">').split('<br><br>')
            item['store_hours'] = {}

            # Need to revisit sanitizing strings of  : , <html_tags>
            for _entity in store_hours:
                
                #Check to prevent any residual html tag from polluting store_hours dict()
                if not re.match('\w+', _entity):
                    break
                _day,_hours = _entity.split(':',1)
                item['store_hours'][_day] = _hours
            
            item['phone'] = _args[-1].strip()
            item['address'] = ''.join(_args[:-1]).strip()            
            item['store_name'] = store_name_list[index].strip()
            item['state'] = store_state
            item['zipcode'] = _args[-2].split(' ')[-1].replace('<br>','')
            item['store_country'] = 'US'
            item['city'] =  _args[-2].split(',')[0].strip()

            items.append(item)
  
        return items