import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TtworiversItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class TtworiversSpider(scrapy.Spider):
	name = 'tworivers'
	start_urls = ['https://www.tworivers.bank/service-support/blogs/']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//span[@class="prev-posts-link"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = "Date is not stated in article"
		title = response.xpath('//h2/text()').get()
		content = response.xpath('(//div[@class="col-md-12"])[last()]//text()[not (ancestor::h2)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TtworiversItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
