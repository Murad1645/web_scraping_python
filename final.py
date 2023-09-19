from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from urllib import parse


class Booking(webdriver.Chrome):
    def __init__(self, driver=None, teardown=False):
        self.teardown = teardown
        if driver is None:
            super().__init__()  # Create a new Chrome driver if one is not provided
        else:
            self.driver = driver

    def __enter__(self):

        self.maximize_window()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.teardown:
            self.quit()

    def land_first_page(self):
        self.get("https://www.booking.com/")  # Correct the URL here

    def cross_botton(self):
        hit = self.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Dismiss sign-in info."]')
        if hit:
            hit.click()

    def change_currency(self):
        # Use self.find_element for locating elements
        currency_button = self.find_element(
            By.XPATH, '//*[@id="b2indexPage"]/div[2]/div/header/nav[1]/div[2]/span[1]/button')
        # Perform actions on the element
        currency_button.click()
        # time.sleep(1)
        select_currency = self.find_element(
            By.CSS_SELECTOR, 'button[data-testid="selection-item"]')
        if select_currency:
            select_currency.click()

    def select_place_to_go(self, place_to_go):
        search_field = self.find_element(By.XPATH, '//*[@id=":re:"]')
        search_field.clear()
        search_field.send_keys(place_to_go)
        time.sleep(1)
        # self.implicitly_wait(5)
        first_result = self.find_element(
            By.XPATH, '//*[@id="indexsearch"]/div[2]/div/form/div[1]/div[1]/div/div/div[2]/div/ul/li[1]')
        time.sleep(1)
        first_result.click()

    def select_dates(self, check_in_date, check_out_date):
        check_in_element = self.find_element(
            By.CSS_SELECTOR, f'span[data-date="{check_in_date}"]')
        if check_in_element:
            check_in_element.click()
        time.sleep(2)
        check_out_element = self.find_element(
            By.CSS_SELECTOR, f'span[data-date="{check_out_date}"]')
        if check_out_element:
            check_out_element.click()

    def select_adult(self, count):
        select_element = self.find_element(
            By.CSS_SELECTOR, 'button[data-testid="occupancy-config"]')
        select_element.click()

        while True:
            decrease_adult = self.find_element(
                By.XPATH, '//*[@id="indexsearch"]/div[2]/div/form/div[1]/div[3]/div/div/div/div/div[1]/div[2]/button[1]')
            decrease_adult.click()
            time.sleep(1)
            adult_value = self.find_element(
                By.ID, 'group_adults').get_attribute('value')

            if int(adult_value) == 1:
                break
        for i in range(count-1):
            increase_button = self.find_element(
                By.XPATH, '//*[@id="indexsearch"]/div[2]/div/form/div[1]/div[3]/div/div/div/div/div[1]/div[2]/button[2]')
            increase_button.click()
        self.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def apply_star_rating(self, star_value):

        star_filtration_box = self.find_element(
            By.XPATH, '/html/body/div[5]/div/div[4]/div[1]/div[2]/div[1]/div/div/div[3]/div[5]')
        star_child_elements = star_filtration_box.find_elements(
            By.CSS_SELECTOR, '*')
        for star_element in star_child_elements:
            if str(star_element.get_attribute('innerHTML')).strip() == f"{star_value} stars":
                star_element.click()

    def adjusting_price(self, new_value):
        url = parse.urlparse(self.current_url)
        qs = parse.parse_qs(url.query)
        qs['nflt'] = f'price%3DUSD-min-{new_value}-1'
        self.get(
            url._replace(
                query=parse.urlencode(qs, doseq=True)
            ).geturl()
        )

    def return_AllInformation(self):
        HotelName_list = []
        Cost = []
        address_list = []
        link_list = []
        review_list = []
        for page in range(1,3):
            page1=self.find_element(By.CSS_SELECTOR,f'button[aria-label=" {page}"]')
            page1.click()
            time.sleep(2)
            for item in self.find_elements(By.CSS_SELECTOR,'#search_results_table [data-testid="property-card"]'): #That's the another way to creat child element.
                    HotelName=item.find_element(By.CSS_SELECTOR,'[data-testid="title"]').text
                    HotelName_list.append(HotelName)

                    link = item.find_element(By.TAG_NAME,'a').get_attribute("href")
                    link_list.append(link)

                    cost=item.find_element(By.CSS_SELECTOR,'[data-testid="price-and-discounted-price"]').text
                    Cost.append(cost)

                    address=item.find_element(By.CSS_SELECTOR,'[data-testid="address"]').text
                    address_list.append(address)

                    review=item.find_element(By.CSS_SELECTOR,'[data-testid="review-score"]').text
                    review_list.append(review)

        alinformation_dict={'Hotel_Name':HotelName_list,'Cost':Cost, 'Address':address_list,'Review':review_list,'link':link_list}
        df = pd.DataFrame(alinformation_dict)
        df.to_csv('Phone.csv',index=False)
        
# Usage
with Booking() as bot:
    bot.land_first_page()

    time.sleep(2)
    bot.cross_botton()
    bot.change_currency()  # Example usage of change_currency method
    time.sleep(2)
    bot.select_place_to_go(input("Where you want to go?"))
    time.sleep(2)
    bot.select_dates(check_in_date=input("What is the check in date?"), check_out_date=input("What is the check out date?"))
    bot.select_adult(int(input("How many people?")))
    time.sleep(1)
    bot.adjusting_price(new_value='500')
    time.sleep(2)
    bot.apply_star_rating(star_value=4)

    time.sleep(3)
    bot.return_AllInformation()

time.sleep(40)
