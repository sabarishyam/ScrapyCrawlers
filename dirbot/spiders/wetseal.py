import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import FormRequest
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector

from dirbot.items import *


class WetsealSpider(Spider):
    name = "wetseal"
    allowed_domains = ["wetseal.com"]
    start_urls = ["http://www.wetseal.com/Stores"]

    def parse(self, response):

        sel = Selector(response)
        form_url = sel.xpath('//form[@id="dwfrm_storelocator_state"]/@action').extract()
        states = sel.xpath('//option[@value]/@value').re(r'[A-Z]+')

        import pdb;pdb.set_trace()

        for state in states:            
            yield FormRequest(form_url,
                            formname='dwfrm_storelocator_state',
                            formdata={'dwfrm_storelocator_address_states_stateUSCA': state,
                                      'dwfrm_storelocator_findbystate': 'Search'},
                            callback=self.parse1)

    def parse1(self, response):
        if "store-name" in response.body:
            import pdb;pdb.set_trace()
        sel = Selector(response)
        
        print response.status