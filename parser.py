from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException

import json

def collect_reviews():

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='/home/alex/Downloads/geckodriver', options=options)
    driver.get("https://eldorado.ua/")

    # categories = driver.find_elements(By.XPATH, ".//div[@class='first-nesting-menu']/div")
    # for category in categories:
    #     category.click()
    #     driver.implicitly_wait(5)
    #     sub_categories = driver.find_elements(By.XPATH, ".//div[@class='title']/a")
    #     for sub_category in sub_categories:
    #         sub_category.click()
    #         driver.implicitly_wait(5)
    #         # kartochka tovara
    #
    #         items = []


            # driver.find_element(By.XPATH, )



    driver.get("https://eldorado.ua/smartphones/c1038946/producer=samsung/")
    urls = []
    links = driver.find_elements(By.XPATH, "//div[@class='image-place']/a")
    for link in links:
        urls.append(link.get_attribute('href'))

    for url in urls:
        driver.get(url)
        review_list = []
        title = driver.find_element(By.XPATH, "//div[@class='product-name']").text

        def load_all_comments():
            try:
                while check_exists_by_xpath(driver, ("//div[@class='load-more-comments']")):
                    try:
                        driver.find_element(By.XPATH, "//div[@class='load-more-comments']").click()
                    except ElementClickInterceptedException:
                        driver.implicitly_wait(10)
            except StaleElementReferenceException:
                print('Stale element ignored')
                driver.refresh()
                load_all_comments()

        reviews = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='current-comment']")))
    #
        for review in reviews:
            driver.implicitly_wait(10)
            author_name = WebDriverWait(review, 10).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='name']"))).text
            date = WebDriverWait(review, 10).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='date']"))).text
            text = WebDriverWait(review, 10).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='comment']"))).text


            review_dict = {
                "title": title,
                "author_name": author_name,
                "url": driver.current_url,
                "grade": 5,
                "date": date,
                "text": text
            }
            review_list.append(review_dict)

        with open("reviews/{}.json".format(driver.find_element(By.XPATH, "//div[@class='product-name']").text.replace('/', ' ')), "w") as write_file:
            json.dump(review_list, write_file, indent=4, ensure_ascii=False)

    driver.quit()


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

if __name__ == '__main__':
    collect_reviews()