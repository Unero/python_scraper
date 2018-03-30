#!F:\Python\python
# -- coding : UTF8 --
# This scraper is created by Unero for "Books" from amazon
from dateutil import parser as dateparser
from fake_useragent import UserAgent
from lxml import html
from time import sleep
import isbnlib
import urllib.request
import json
import re
import requests

 
def amazon(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    page = requests.get(url, headers=headers)
    while True:
        sleep(3)
        try:
            parser_page = html.fromstring(page.content)
            raw_title = parser_page.xpath('//span[@id="productTitle"]//text()')
            raw_price = parser_page.xpath('//span[@class="a-size-medium a-color-price offer-price a-text-normal"]'
                                          '//text()')
            raw_sale = parser_page.xpath('//span[@class="a-size-base a-color-secondary"]//text()')
            raw_author = parser_page.xpath('//a[@class="a-link-normal contributorNameID"]//text()')
            raw_category = parser_page.xpath('//a[@class="a-link-normal a-color-tertiary"]//text()')
            raw_availability = parser_page.xpath('//div[@id="availability"]//text()')
            ratings = parser_page.xpath('//table[@id="histogramTable"]//tr')
            reviews = parser_page.xpath('//div[contains(@id,"reviews-summary")]')

            title = ''.join(''.join(raw_title).strip()) if raw_title else None
            sale = ''.join(''.join(raw_sale).split()).strip() if raw_sale else None
            category = ' > '.join([i.strip() for i in raw_category]) if raw_category else None
            price = ''.join(raw_price).strip() if raw_price else None
            availability = ''.join(raw_availability).strip() if raw_availability else None
            review_author = ''.join(raw_author).strip() if raw_author else None

            title_to_isbn = str(title)
            isbn = isbnlib.isbn_from_words(title_to_isbn)
            desc = str(isbnlib.desc(isbn))
            description = ''.join(desc).strip() if desc else None
            isbn10 = isbnlib.to_isbn10(isbn)
            raw_isbn13 = isbn[:3] + '-' + isbn[3:]
            isbn_13 = ''.join(raw_isbn13).strip() if raw_isbn13 else None
            isbn_10 = ''.join(isbn10).strip() if isbn10 else None

            if not reviews:
                reviews = parser_page.xpath('//div[@data-hook="review"]')

            # Rating
            ratings_dict = {}
            for ratings in ratings:
                extracted_rating = ratings.xpath('./td//a//text()')
                if extracted_rating:
                    rating_key = extracted_rating[0]
                    raw_rating_value = extracted_rating[1]
                    rating_value = raw_rating_value
                    if rating_key:
                        ratings_dict.update({rating_key: rating_value})

            # Reviews
            reviews_list = []
            for review in reviews:
                raw_review_header = review.xpath('.//a[@data-hook="review-title"]//text()')
                raw_review_author = review.xpath('.//a[contains(@href,"/profile/")]/parent::span//text()')
                raw_review_rating = review.xpath('.//i[@data-hook="review-star-rating"]//text()')
                raw_review_posted_date = review.xpath('.//a[contains(@href,"/profile/")]'
                                                      '/parent::span/following-sibling::span/text()')
                raw_review_text1 = review.xpath('.//div[@data-hook="review-collapsed"]//text()')
                raw_review_text2 = review.xpath('.//div//span[@data-action="columnbalancing-showfullreview"]'
                                                '/@data-columnbalancing-showfullreview')
                raw_review_text3 = review.xpath('.//div[contains(@id,"dpReviews")]/div/text()')

                review_header = ' '.join(' '.join(raw_review_header).split())
                review_author = ''.join(''.join(raw_review_author).split()).strip('By')
                review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
                review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
                review_text = ' '.join(' '.join(raw_review_text1).split())

                if raw_review_text2:
                    json_loaded_review_data = json.loads(raw_review_text2[0])
                    json_loaded_review_data_text = json_loaded_review_data['rest']
                    cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                    full_review_text = review_text + cleaned_json_loaded_review_data_text
                else:
                    full_review_text = review_text
                if not raw_review_text1:
                    full_review_text = ' '.join(' '.join(raw_review_text3).split())

                review_dict = {
                    'review_header': review_header,
                    'review_author': review_author,
                    'review_rating': review_rating,
                    'review_posted_date': review_posted_date,
                    'review_text': full_review_text,

                }
                reviews_list.append(review_dict)

            if not price:
                price = sale

            if page.status_code != 200:
                raise ValueError('captha')

            data = {
                    'URL': url,
                    'TITLE': title,
                    'AUTHOR': review_author,
                    'PRICE': price,
                    'SALE': sale,
                    'CATEGORY': category,
                    'DESCRIPTION': description,
                    'ISBN-10': isbn_10,
                    'ISBN-13': isbn_13,
                    'AVAILABILITY': availability,
                    'RATING': ratings_dict,
                    'REVIEW': reviews_list,
                    }
 
            return data
        except Exception as e:
            print(e)
            if e == 'NoneType':
                return None
 

def crawler():
    with open('asin.txt', 'r'):
        asin_list = [line.strip() for line in open('asin.txt')]
    extracted_data = []
    for i in asin_list:
        url = "http://www.amazon.com/dp/"+i
        cover_url = "http://z2-ec2.images-amazon.com/images/P/" + i + ".jpg"
        cover_name = i + ".jpg"
        print("Processing: "+url)
        extracted_data.append(amazon(url))
        urllib.request.urlretrieve(cover_url, cover_name)
        sleep(15)
    f = open('data.json', 'w')
    json.dump(extracted_data, f, indent=4)


if __name__ == "__main__":
    crawler()