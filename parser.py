from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

import json

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def collect_urls(driver, xpath):

    urls = []
    urls_web_elements = []

    elements = driver.find_elements(By.XPATH, xpath)
    for i in elements:
        urls_web_elements.append(i)
    for i in urls_web_elements:
        urls.append(i.get_attribute("href"))

    return urls


def collect_reviews(driver):
    return_list = []
    reviews = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions) \
        .until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='current-comment']")))
    title = driver.find_element(By.XPATH, "//div[@class='product-name']").text
    for review in reviews:
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
        except StaleElementReferenceException:
            print("Stale in {}".format(driver.current_url))
            return collect_reviews(driver)
    return return_list


def reviews_per_item(driver, page_url):
    driver.get(page_url)
    review_list = []

    if check_exists_by_xpath(driver, "//div[@class='current-comment']"):
        if check_exists_by_xpath(driver, "//ul[@class='text-n-o-c pages']"):
            while check_exists_by_xpath(driver, "//div[@class='back_pagin disabled-arrow']") is False:
                reviews = collect_reviews(driver)
                for i in reviews:
                    review_list.append(i)
                try:
                    driver.find_element(By.XPATH, "//div[@class='back_pagin']").click()
                except NoSuchElementException:
                    break
                driver.implicitly_wait(1)

            reviews = collect_reviews(driver)
            for i in reviews:
                review_list.append(i)
        else:
            reviews = collect_reviews(driver)
            for i in reviews:
                review_list.append(i)

        with open("reviews/{}.json".format(
                driver.find_element(By.XPATH, "//div[@class='product-name']").text.replace('/', ' ')),
                  "a") as write_file:
            json.dump(review_list, write_file, indent=4, ensure_ascii=False)
    else:
        print("No comments for {}".format(driver.current_url))


def reviews_per_sub_category(driver, page_url):
    driver.get(page_url)
    urls = []

    # go thought pagination pages and collect all urls
    if check_exists_by_xpath(driver, "//ul[@class='text-n-o-c pages']"):
        while check_exists_by_xpath(driver, "//div[@class='back_pagin disabled-arrow']") is False:
            for url in collect_urls(driver, "//div[@class='image-place']/a"):
                urls.append(url)
            driver.find_element(By.XPATH, "//div[@class='back_pagin']").click()
        for url in collect_urls(driver, "//div[@class='image-place']/a"):
            urls.append(url)
    else:
        for url in collect_urls(driver, "//div[@class='image-place']/a"):
            urls.append(url)

    for url in urls:
        reviews_per_item(driver, url)


def reviews_per_category(driver, page_url):
    driver.get(page_url)
    pages = collect_urls(driver, "//div[@class='node-item']/div/a")
    for page in pages:
        reviews_per_sub_category(driver, page)


if __name__ == '__main__':
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='/home/alex/Downloads/geckodriver', options=options)
    driver.get("https://eldorado.ua/")
    pages = collect_urls(driver, "//div[@class='main-category']//a")
    for index, page in enumerate(pages):
        reviews_per_category(driver, page)
        if index == 3:
            break
    driver.quit()
