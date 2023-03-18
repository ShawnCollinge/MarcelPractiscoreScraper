import re, time
from selenium import webdriver
from bs4 import BeautifulSoup

url = "https://practiscore.com/results/new/e6f1e756-9f03-477e-94e0-c37aa5ad64d2"

driver = webdriver.Firefox()
driver.get(url)
html = driver.page_source
MySoup = BeautifulSoup(html, "html.parser")
results = MySoup.find_all(name="a", class_="shooterLink")
for result in results:
    if "Tan" in result.getText():
        print(result.getText())
driver.close()