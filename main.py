import requests
from parsel import Selector
from database import Database


class AutoRiaScraper:
    START_URL = "https://auto.ria.com/car/used/?page={}"
    TEXT = requests.get(START_URL).text
    SELECTOR = Selector(text=TEXT)
    LINK = '//head/link[@rel="amphtml"]/@href'
    TITLE = "//h1/text()"
    USD_PRICE = "//div[@class='price_value']/strong/text()"
    MILE_AGE = "span.size18::text"
    USERNAME = "h4.seller_info_name.bold::text"
    PHONE = "div.popup-successful-call-desk.size24.bold.green.mhide.green::text"
    IMAGE_URL = '//div[contains(@class, "carousel-inner")]/div[1]//img/@src'
    TOTAL_IMAGE_COUNT = '//span[@class="count"]/span[@class="mhide"]/text()'
    CAR_NUMBER = '//span[@class="state-num ua"]/text()'
    VIN_CODE = '//span[@class="vin-code"]//text()'
    ALT_VIN_CODE = "//span[@class='label-vin']//text()"
    all_pages = []
    all_auto_url = []
    ALL_AUTO_URL = '//a[@class="address"]/@href'
    ALLOW_STATUS_CODES = [200]
    RETRIES = 5

    def __init__(self) -> None:
        self.database = Database()

    def get_all_pages(self) -> None:
        for page in range(1, 21):
            self.all_pages.append(self.START_URL.format(page))
            for item in self.all_pages:
                self.all_auto_url.extend(
                    self.SELECTOR.xpath(self.ALL_AUTO_URL).extract()
                )

    def parse_data(self) -> None:
        for auto in self.all_auto_url:
            new_text = requests.get(auto).text
            new_selector = Selector(text=new_text)
            link = new_selector.xpath(self.LINK).get()
            title = new_selector.xpath(self.TITLE).get()
            usd_price = new_selector.xpath(self.USD_PRICE).get()
            mile_age = new_selector.css(self.MILE_AGE).get() + " тыс. км пробег"
            username = new_selector.css(self.USERNAME).get()
            phone_number = new_selector.css(self.PHONE).get()
            img_url = new_selector.xpath(self.IMAGE_URL).get()
            finder_total = new_selector.xpath(self.TOTAL_IMAGE_COUNT).get()
            img_total_count = finder_total[3:]
            car_number = new_selector.xpath(self.CAR_NUMBER).get()
            vin_code = "".join(new_selector.xpath(self.VIN_CODE).extract())
            if vin_code == "":
                vin_code = "".join(new_selector.xpath(self.ALT_VIN_CODE).extract())

            data = {
                "url": link,
                "title": title,
                "usd_price": usd_price,
                "mile_age": mile_age,
                "username": username,
                "phone_number": phone_number,
                "img_url": img_url,
                "img_total_count": img_total_count,
                "car_number": car_number,
                "car_vin_code": vin_code,
            }

            self.database.insert_data(data=data)
            print(data)

    def main(self) -> None:
        self.get_all_pages()
        self.parse_data()


if __name__ == "__main__":
    scraper = AutoRiaScraper()
    scraper.main()
