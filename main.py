import csv
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_data(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }

    req = requests.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(file='data/index.html', mode='w', encoding='utf-8') as file:
        file.write(req.text)


    with open(file='data/index.html', mode='r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    unlock_pagination = int(soup.find('div'
                                      , class_='bx-pagination-container').find_all('a')[-2].text)

    for i in range(1, unlock_pagination + 1):
        url = f'https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/?PAGEN_1={i}'

        req = requests.get(url=url, headers=headers)

        with open(file=f'data/page_{i}.html', mode='w', encoding='utf-8') as file:
            file.write(req.text)

        time.sleep(2)

    return unlock_pagination + 1


def collect_data(pages_data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    with open(file=f"data_{cur_date}.csv", mode="w", encoding='utf-8', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Артикул",
                "Ссылка",
            )
        )

    data = []
    for page in range(1, pages_data):
        with open(file=f'data/page_{page}.html', mode='r', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        items_card = soup.find_all('a', class_='product-item__link')

        for item in items_card:
            product_article = item.find('p', class_='product-item__articul').text.strip()
            product_url = 'https://shop.casio.ru' + item.get('href')
            data.append(
                {
                    'product_article': product_article,
                    'product_url': product_url
                }
            )

            with open(file=f"data_{cur_date}.csv", mode="a", newline='') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        product_article,
                        product_url,
                    )
                )

        print(f"[INFO] обработанная страница {page}/{pages_data - 1}")

    with open(file=f'data_{cur_date}.json', mode='w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    pages_data = get_data(url='https://shop.casio.ru/catalog/g-shock/filter/gender-is-male/apply/')
    collect_data(pages_data)

if __name__ == '__main__':
    main()