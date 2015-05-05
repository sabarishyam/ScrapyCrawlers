import urlparse
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.item import Item, Field

class Hhgreg(Item):

    currency = Field()
    current_price = Field()
    original_price = Field()
    store_services = Field()
    description = Field()
    brand = Field()
    title = Field()
    retailer_id = Field()
    model = Field()
    mpn = Field()
    sku = Field()
    upc = Field()
    
    # No luck with the image Url's. With a little time I mgight figure it out but
    # I guess  im running out of time 
    #image_url = Field()

    primary_image_url = Field()
    features = Field()
    specifications = Field()

    # Not sure what Trail implies 
    #trail = Field()
    
    rating = Field()
    
    # Unless a pincode is provided, it isn't possible to say if the product is availabe or not.
    # Request URL:http://www.hhgregg.com/webapp/wcs/stores/servlet/AjaxCheckProductAvailabilityService
    # method POST
    # Url aprams: storeId=10154&catalogId=10051&langId=-1&zipCode=10008&partnum=211290&quantity=1&requesttype=ajax
    #availabe_instore = Field()

    #I couldnt find a div or a container that matches the available_online field
    #availabe_online = Field()

class HhgregSpider(CrawlSpider):

    name = "hhgreg"
    rules = [
        Rule(LxmlLinkExtractor(), callback='parse_obj', follow='True')
        ]
    allowed_domains = ["hhgregg.com"]

    start_urls = [
        "http://www.hhgregg.com"
    ]

    def parse_obj(self, response):

        if 'item' not in response.url:
            return

        sel = Selector(response)

        items = Hhgreg()

        try:

            #Retailer Id
            items['retailer_id'] =  sel.xpath('//input[@name="storeId"]/@value').extract()[0].strip()

            #Product Id
            items['sku'] =  sel.xpath('//input[@name="catalogId"]/@value').extract()[0].strip()

            #Current Price
            items['current_price'] = sel.xpath('//span[@class="price spacing"]/text()').extract()[0].strip()

            
            # Most items dont have an original price
            #Original Price
            try:
                original_price = sel.xpath('//div[@class="reg_price strike-through"]/span/text()').extract()[1].strip()
                items['original_price'] = original_price
            except Exception, e:
                items['original_price'] = items['current_price']
                pass

            #Currency
            items['currency'] = items['current_price'][0]

            #Description
            items['description'] = sel.xpath('//meta[@property="og:description"]/@content').extract()[0].strip()

            #Title
            items['title'] = sel.xpath('//meta[@property="og:title"]/@content').extract()[0].strip()

            #Primary_image_url
            items['primary_image_url'] = sel.xpath('//meta[@property="og:image"]/@content').extract()[0].strip()

            #Just a safety to make sure we dont throw NoneType attribute erros while extracting brand

            #Brand
            try:
                brand = re.search(r'model_name(.*)=(.*)', response.body).group(0)
                items['brand'] = re.search(r'[-\w]+',brand.split('=')[1]).group(0)
            except Exception,e:
                items['brand'] = ''
                pass

            #Model Number
            try:
                model = re.search(r'entity.id(.*)=(.*)', response.body).group(0)
                items['model'] = re.search(r'[-\w]+',model.split('=')[1]).group(0)
            except Exception,e:
                items['model'] = ''
                pass


            #MPN
            try:
                mpn = re.search(r'entity.message(.*)=(.*)', response.body).group(0)
                items['mpn'] = re.search(r'[-\w]+',mpn.split('=')[1]).group(0)
            except Exception,e:
                items['mpn'] = ''
                pass

            #UPC
            try:
                upc = re.search(r'entity.categoryId(.*)=(.*)', response.body).group(0)
                items['upc'] = re.search(r'[-\w]+',upc.split('=')[1]).group(0)
            except Exception,e:
                items['upc'] = ''
                pass
            
            #Rating
            try:
                items['rating'] = sel.xpath('//span[@class="pr-rating pr-rounded average"]/text()').extract()[0]
                items['rating'] = float(items['rating'])/5 *100
            except Exception,e:
                items['rating'] = ''

            #Features
            items['features'] =''
            features = sel.xpath('//div[@class="features_list"]/ul/li/span').extract()
            for feature in features:
                items['features'] += re.sub(r'<[\w\s="/]+>','',feature)

            #Specifications
            items['specifications'] = {}
            spec_keys = sel.xpath('//span[@class="specdesc"]//span[@class="dotted"]/text()').extract()
            spec_values = sel.xpath('//span[@class="specdesc"]//span[@class="dotted"]/text()').extract()
            try:                
                for i,key in enumerate(spec_keys):
                    items['specifications'][key.strip(':')] = spec_values[i].strip()
            except:
                # Maybe missing spec elements
                pass

            
        except:
            pass

        return items
