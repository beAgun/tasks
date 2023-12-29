import os.path
import time
import datetime
import csv
from math import floor
import random

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_date(driver, element):
    element = element.find_element(By.CLASS_NAME, "echo_date")
    attrs = driver.execute_script(
        'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
        element)
    return datetime.datetime.strptime(attrs['data-published'],
                                      '%Y-%m-%dT%H:%M:%S+03:00')


def get_title_and_link(driver, element):
    element = element.find_element(By.TAG_NAME, 'a')
    attrs = driver.execute_script(
        'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
        element)
    link = attrs['href']
    return element.text, link


def get_description(element):
    element = element.find_element(By.CLASS_NAME, "news-item-excerpt")
    return element.text


def collect_data(file, elements, date, driver):

    def add_item(date_element, element):
        data = str(date_element) + '|'
        title, link = get_title_and_link(driver, element)
        description = get_description(element)
        data += title + '|' + description + '|' + link
        with open(file, 'a', encoding='utf-8') as f:
            f.write(data + '\n')

    cnt = 0
    for element in elements:
        date_element = get_date(driver, element)
        if date_element.date() == date.date():
            add_item(date_element, element)
            cnt += 1

    if cnt:
        return 1


def find_data(url, date, file):

    cur_date = datetime.datetime.now()
    dif_days = (cur_date - date).days
    if dif_days < 0:
        print('No such date yet')
        return

    magic_number = 2.5

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.get(url)
    time.sleep(3)
    xpath = '//div[@class="pagination-block"]//a[@class="page-numbers"]'
    elements = driver.find_elements(By.XPATH, xpath)
    last_page_number = int(elements[-1].text.replace(' ', ''))
    first_page_number = 0

    # def rec(first_page_number, last_page_number, visited=None):
    #     if visited is None:
    #         visited = []
    #     print(first_page_number, last_page_number,  type(first_page_number), type(last_page_number))
    #     page_number = floor((first_page_number + last_page_number) / 2)
    #
    #     if page_number in visited:
    #         return
    #     visited += [page_number]
    #
    #     new_url = url + '/page/' + str(page_number)
    #     driver.get(url=new_url)
    #     time.sleep(3)
    #
    #     xpath = '//div[@class="news-item grid"]'
    #     elements = driver.find_elements(By.XPATH, xpath)
    #
    #     element_first, element_last = elements[0], elements[-1]
    #     date_first, date_last = get_date(driver, element_first), get_date(driver, element_last)
    #
    #     if date_first.date() >= date.date() >= date_last.date():
    #         if not collect_data(file, elements, date, driver):
    #             return
    #
    #         if date_first.date() == date.date() != cur_date.date():
    #             rec(page_number - 1,  file, visited)
    #
    #         if date_last.date() == date.date():
    #             rec(page_number + 1, file, visited)
    #
    #     elif date.date() < date_first.date():
    #         rec(page_number + 1, last_page_number, visited)
    #
    #     elif date.date() > date_last.date() and date.date() != cur_date.date():
    #         rec(first_page_number, page_number - 1, visited)
    #
    # rec(1, last_page_number, None)

    try:
        def rec(page_number, file, visited=None):
            if visited is None:
                visited = []

            while True:
                if page_number in visited:
                    break
                visited += [page_number]

                new_url = url + '/page/' + str(page_number)
                driver.get(url=new_url)
                time.sleep(3)

                xpath = '//div[@class="news-item grid"]'  # "//div[@class = 'content']//span[contains(concat(' ', normalize-space(@class), ' '), 'echo_date')]"
                elements = driver.find_elements(By.XPATH, xpath)

                element_first, element_last = elements[0], elements[-1]
                date_first, date_last = get_date(driver, element_first), get_date(driver, element_last)

                if date_first.date() >= date.date() >= date_last.date():
                    if not collect_data(file, elements, date, driver):
                        break

                    if date_first.date() == date.date():
                        rec(max(first_page_number, page_number - 1), file, visited)

                    if date_last.date() == date.date():
                        rec(min(page_number + 1, last_page_number), file, visited)

                    break

                elif date.date() < date_last.date():
                    if page_number == last_page_number:
                        print('That was a long time ago')
                        return

                    res = int((date_last - date).days // magic_number)
                    if res == 0:
                        page_number += min(page_number + 1, last_page_number)
                    else:
                        page_number = min(page_number + res, last_page_number)

                elif date.date() > date_first.date():

                    res = int((date - date_first).days // magic_number)
                    if res == 0:
                        page_number = max(first_page_number, page_number - 1)
                    else:
                        page_number = max(first_page_number, page_number - res)

        page_number = min(int(dif_days // magic_number), last_page_number)
        rec(page_number, file, None)

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


def reformat(file_name):

    data = []
    with open(f'{file_name}.txt', 'r', encoding='utf-8') as inf:
        for line in inf:
            date, title, description, link = line.split('|')
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            link.replace('\n', '')
            data += [(date, title, description, link)]
    os.remove(f'{file_name}.txt')

    data = sorted(data)
    with open(f'{file_name}.csv', 'a', encoding='utf-8') as outf:
        header = ['Publication Date', 'Title', 'Description', 'Link']
        writer = csv.writer(outf, delimiter=',')
        writer.writerow(i for i in header)
        for item in data:
            writer.writerow(i for i in item)


def main():
    #date = '2023-03-25'

    date = input('Input a date to find science news. Format: YYYY-M-D: ')
    file_name = ''
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        file_name = f'{str(date.date())}'
    except ValueError:
        print('Incorrect format')
        return

    if os.path.exists(f'{file_name}.csv'):
        #file_name += '-2'
        os.remove(f'{file_name}.csv')

    find_data(
        url='https://naked-science.ru/article', date=date, file=f'{file_name}.txt')

    if not os.path.exists(f'{file_name}.txt'):
        print('Nothing found')
        return

    reformat(file_name)


if __name__ == "__main__":
    main()