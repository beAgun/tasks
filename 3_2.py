import os.path
import time
import datetime
import csv
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

    if cnt == 0:
        return 0


def find_data(url, date, file_name):

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

    try:

        def rec(page_number, file, visited_first_dates=None):
            if visited_first_dates is None:
                visited_first_dates = []
            while True:
                if page_number > 1064:
                    print('That was a long time ago...')
                    return
                new_url = url + '/page/' + str(page_number)
                driver.get(url=new_url)
                time.sleep(3)

                xpath = '//div[@class="news-item grid"]'
                # "//div[@class = 'content']//span[contains(concat(' ', normalize-space(@class), ' '), 'echo_date')]"
                # '//div[@class = "content"]//span[@class = "echo_date"]'
                elements = driver.find_elements(By.XPATH, xpath)

                element_first = elements[0]
                element_last = elements[-1]
                date_first = get_date(driver, element_first)
                date_last = get_date(driver, element_last)

                if (date_first, date_last) in visited_first_dates:
                    break
                else:
                    visited_first_dates += [(date_first, date_last)]

                if date_first.date() >= date.date() >= date_last.date():
                    ans = collect_data(file, elements, date, driver)
                    if ans == 0:
                        break

                    if date_first.date() == date.date():
                        rec(page_number - 1, file, visited_first_dates)

                    if date_last.date() == date.date():
                        rec(page_number + 1, file, visited_first_dates)

                    break

                elif date.date() < date_first.date():
                    res = int((date_first - date).days // magic_number)
                    if res < 2:
                        page_number += 1
                    else:
                        page_number += res
                elif date.date() > date_last.date():
                    res = int((date - date_last).days // magic_number)
                    if res < 2:
                        page_number -= 1
                    else:
                        page_number -= res

        page_number = int(dif_days // 2.5)
        rec(page_number, file_name, None)

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
    date = '2023-03-25'

    date = input('Input a date to find science news. Format: YYYY-M-D: ')
    file_name = ''
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        file_name = f'{str(date.date())}'
    except ValueError:
        print('Incorrect format')
        return

    if os.path.exists(f'/{file_name}.txt'):
        os.remove(f'{file_name}.txt')
        return

    find_data(
        url='https://naked-science.ru/article', date=date, file_name=f'{file_name}.txt')

    if not os.path.exists(f'{file_name}.txt'):
        print('Nothing found')
        return

    reformat(file_name)


if __name__ == "__main__":
    main()