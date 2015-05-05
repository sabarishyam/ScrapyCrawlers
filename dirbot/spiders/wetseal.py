import urlparse
import re

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
    store_hours = Field()
    store_name = Field()
    phone = Field()
    state = Field()
    store_id = Field()
    zipcode = Field()

    #Couldnot find the following fields in tghe HTML page

    #store_services = Field() 
    #store_image_url = Field()
    #store_url = Field()
    #store_email = Field()
    #store_floor_plan_url = Field()
    #weekly_ad_url = Field()

class WetsealSpider(Spider):
    name = "wetseal"
    allowed_domains = ["wetseal.com"]
    start_urls = ["http://www.wetseal.com/Stores"]

    def parse(self, response):

        sel = Selector(response)
        form_url = sel.xpath('//form[@id="dwfrm_storelocator_state"]/@action').extract()
        states = sel.xpath('//option[@value]/@value').re(r'[A-Z]+')

        for state in states:            
            yield FormRequest(url=''.join(form_url),
                            formdata={'dwfrm_storelocator_address_states_stateUSCA': state,
                                      'dwfrm_storelocator_findbystate': 'Search'},
                            callback=self.parse1)

    def parse1(self, response):

        sel = Selector(response)
        items = []      

        try:
            #Store address selector
            store_address_list =  sel.xpath('//td[@class="store-address"]')

            #Store name selector
            store_name_list = sel.xpath('//div[@class="store-name"]/text()').extract()

            #Store hours selector
            store_hours_args = sel.xpath('//div[@class="store-hours"]')

            #Fetch the Store state
            store_state = response.request.body.split('=')[-1]

            for index,address in enumerate(store_address_list):
                
                item = Wetseal()
                _args = address.extract().replace('\t','').split('\n')[1:-1]
                
                store_hours = regex.sub('', store_hours_args[index].extract()).strip('<div class="store-hours">').split('<br><br>')
                item['store_hours'] = {}

                # Parse Store hours to match a dict
                for _entity in store_hours:
                    
                    #Check to prevent any residual html tag from polluting store_hours dict()
                    if not re.match('\w+', _entity):
                        break
                    _day,_hours = _entity.split(':',1)
                    item['store_hours'][_day] = _hours.replace('</','').strip()
                
                #Store Phone number
                item['phone'] = _args[-1].strip()

                #Store Address
                item['address'] = ''.join(_args[:-1]).strip()

                #Store Name         
                item['store_name'] = store_name_list[index].strip()

                #Store State
                item['state'] = store_state

                #Store Zipcode
                item['zipcode'] = _args[-2].split(' ')[-1].replace('<br>','')

                #Store Country
                #US because all the zipcodes were self-contained to USA
                item['store_country'] = 'US'

                #Store City
                item['city'] =  _args[-2].split(',')[0].strip()

                items.append(item)

        except Exception,e:
            #Ignore if there any exceptions parsing the response body
            pass
  
        return items