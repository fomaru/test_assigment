from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException

import json

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def collect_reviews(driver):
    return_list = []
    reviews = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions) \
        .until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='current-comment']")))
    title = driver.find_element(By.XPATH, "//div[@class='product-name']").text
    for review in reviews:
        # author_name = WebDriverWait(review, 5, ignored_exceptions=ignored_exceptions) \
        #     .until(EC.presence_of_element_located((By.XPATH, ".//div[@class='name']"))).text
        # # grade = len(review.find_elements(By.XPATH, ".//span[@class='full-stars']"))
        # grade = 5
        # date = WebDriverWait(review, 5, ignored_exceptions=ignored_exceptions) \
        #     .until(EC.presence_of_element_located((By.XPATH, ".//div[@class='date']"))).text
        # text = WebDriverWait(review, 5, ignored_exceptions=ignored_exceptions) \
        #     .until(EC.presence_of_element_located((By.XPATH, ".//div[@class='comment']"))).text
        try:
            author_name = review.find_element(By.XPATH, ".//div[@class='name']").text
            grade = len(review.find_elements(By.XPATH, ".//span[@class='full-stars']"))
            date = review.find_element(By.XPATH, ".//div[@class='date']").text
            text = review.find_element(By.XPATH, ".//div[@class='comment']").text

            review_dict = {
                "title": title,
                "author_name": author_name,
                "url": driver.current_url,
                "grade": grade,
                "date": date,
                "text": text
            }

            return_list.append(review_dict)
            return return_list

        except StaleElementReferenceException:
            collect_reviews(driver)


def reviews_per_category(driver, page_url):
    driver.get(page_url)
    urls = []

    while check_exists_by_xpath(driver, "//div[@class='back_pagin disabled-arrow']") is False:
        if check_exists_by_xpath(driver, "//ul[@class='text-n-o-c pages']"):
            urls_web_elements = driver.find_elements(By.XPATH, "//div[@class='image-place']/a")
            for i in urls_web_elements:
                urls.append(i.get_attribute("href"))
            driver.find_element(By.XPATH, "//div[@class='back_pagin']").click()
            urls_web_elements = driver.find_elements(By.XPATH, "//div[@class='image-place']/a")
        urls_web_elements = driver.find_elements(By.XPATH, "//div[@class='image-place']/a")
    for i in urls_web_elements:
        urls.append(i.get_attribute("href"))

    for url in urls:
        driver.get(url)
        review_list = []
        if check_exists_by_xpath(driver, "//div[@class='current-comment']"):
            if check_exists_by_xpath(driver, "//ul[@class='text-n-o-c pages']"):
                while check_exists_by_xpath(driver, "//div[@class='back_pagin disabled-arrow']") is False:
                    review_list.append(collect_reviews(driver))
                    driver.find_element(By.XPATH, "//div[@class='back_pagin']").click()
                    # driver.implicitly_wait(5)
                review_list.append(collect_reviews(driver))
            else:
                review_list.append(collect_reviews(driver))

            with open("reviews/{}.json".format(driver.find_element(By.XPATH, "//div[@class='product-name']").text.replace('/', ' ')), "w") as write_file:
                json.dump(review_list, write_file, indent=4, ensure_ascii=False)
        else:
            print("No comments for {}".format(driver.current_url))


if __name__ == '__main__':
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(executable_path='/home/alex/Downloads/geckodriver', options=options)
    reviews_per_category(driver, "https://eldorado.ua/tablet-pc/c1039006/producer=lenovo/")
    driver.quit()