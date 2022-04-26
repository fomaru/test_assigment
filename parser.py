from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import json

def collect_reviews():

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='/home/alex/Downloads/geckodriver', options=options)
    driver.get("https://eldorado.ua/")

    driver.find_element(By.XPATH, "//div[@class='main-category'][1]").click()
    driver.implicitly_wait(2)
    driver.find_element(By.XPATH, "(//div[@class='title']/a)[1]").click()
    driver.implicitly_wait(4)
    driver.find_element(By.XPATH, "(//div[@class='goods-item-content'])[1]").click()
    reviews = driver.find_elements(By.XPATH, "//div[@class='current-comment']")

    review_list = []

    for review in reviews:
        review_dict = {
            "title": driver.find_element(By.XPATH, "//div[@class='product-name']").text,
            "author_name": review.find_element(By.XPATH, ".//div[@class='name']").text,
            "url": driver.current_url,
            "grade": 5,
            "date": review.find_element(By.XPATH, ".//div[@class='date']").text,
            "text": review.find_element(By.XPATH, ".//div[@class='comment']").text
        }
        review_list.append(review_dict)

    with open("reviews/data_file.json", "w") as write_file:
        json.dump(review_list, write_file, indent=4, ensure_ascii=False)

    driver.quit()

if __name__ == '__main__':
    collect_reviews()