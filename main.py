from parsel import Selector
import requests
from datetime import datetime
from config import config
import psycopg2


def db_connection():
    global cur, conn
    conn = None
    try:
        params = config()

        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        print("PostgreSQL database version:")
        cur.execute("SELECT version()")

        db_version = cur.fetchone()
        print(db_version)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


class AutoParser:
    start_url = "https://auto.ria.com/car/used/?page={}"
    text = requests.get(start_url).text
    selector = Selector(text=text)
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

    def __init__(self) -> None:
        pass

    def get_all_pages(self):
        for page in range(1, 21):
            self.all_pages.append(self.start_url.format(page))
            for item in self.all_pages:
                self.all_auto_url.extend(
                    self.selector.xpath(self.ALL_AUTO_URL).extract()
                )

    def parse_data(self):
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
            date_found = datetime.utcnow()
            print(
                link,
                title,
                usd_price,
                mile_age,
                username,
                phone_number,
                img_url,
                img_total_count,
                car_number,
                vin_code,
                date_found,
            )
            cur.execute(
                """INSERT INTO auto (url, title, usd_price, mile_age, username, phone_number, img_url, img_total_count, car_number, car_vin_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    link,
                    title,
                    usd_price,
                    mile_age,
                    username,
                    phone_number,
                    img_url,
                    img_total_count,
                    car_number,
                    vin_code,
                ),
            )
            conn.commit()


if __name__ == "__main__":
    db_connection()
    auto = AutoParser()
    print(auto.get_all_pages())
    print(auto.parse_data())
