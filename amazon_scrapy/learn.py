import scrapy


class TitleSpider(scrapy.Spider):
    title = 'title'
    start_urls = [
            'https://www.amazon.com/Automate-Boring-Stuff-Python-2nd/dp/1593279922',
            ]

    def parse(self, response):
        for title in response.css('div.a-section a-spacing-none'):
            yield {
                    'Title': title.css('span.productTitle::text').get(),
                    }

