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
    #store_email = Field()
    #store_floor_plan_url = Field()
    #store_id = Field()
    #weekly_ad_url = Field()
    zipcode = Field()
