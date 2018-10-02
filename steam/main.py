#!F:\Python\python
# -- coding : UTF8 --
# This scraper is created by Unero for scraping user status in steam.
from time import sleep
import requests
from fake_useragent import UserAgent
from lxml import html


def steam(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    page = requests.get(url, headers=headers)
    while True:
        sleep(3)
        try:
            parser_page = html.fromstring(page.content)
            raw_nickname = parser_page.xpath('//div[@class="persona_name"]/span[@class="actual_persona_name"]/text()')
            raw_name = parser_page.xpath('//div[@class="header_real_name ellipsis"]/bdi/text()')
            """
            raw_national = parser_page.xpath('//span[@id="productTitle"]//text()')
            raw_s_level = parser_page.xpath('//span[@id="productTitle"]//text()')
            raw_status = parser_page.xpath('//span[@id="productTitle"]//text()')
            raw_game_owned = parser_page.xpath('//span[@id="productTitle"]//text()')
            raw_comment = parser_page.xpath('//span[@id="productTitle"]//text()')
            """

            if page.status_code != 200:
                raise ValueError('Status page code is not 200!')

            data = {
                'URL': url,
                'NICKNAME': raw_nickname,
                'NAME': raw_name,
            }

            return data

        except Exception as e:
            print(e)
            if e == 'NoneType':
                return None


def crawler():
    extracted_data = []
    user = input("Your Username: ")
    url = "http://www.steamcommunity.com/id/" + user
    print("Processing: " + url)
    extracted_data.append(steam(url))
    sleep(5)
    print(extracted_data)
    # f = open('data.json', 'w')
    # json.dump(extracted_data, f, indent=4)


if __name__ == "__main__":
    crawler()