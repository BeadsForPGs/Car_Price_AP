#get all the values of all values from https://kolesa.kz/a/show/148198404/ and map them together, where key is class="value-title" and value is class="value"
import requests
from bs4 import BeautifulSoup

headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.2.261 Yowser/2.5 Safari/537.36'
        }
request = requests.get("https://kolesa.kz/a/show/148198404", headers=headers)
soup = BeautifulSoup(request.content, 'html.parser')
#put all values in a dictionary
keys = []
values = []
keys.append("Бренд")
values.append(soup.find('span', itemprop="brand").text.strip())
keys.append("Модель")
values.append(soup.find('span', itemprop="name").text.strip())
keys.append("Год выпуска")
values.append(int(soup.find('span', class_="year").text.strip()))
keys.append("Цена")
values.append(
    int(soup.find('div', class_="offer__price").text.strip().replace('\xa0', '').replace('\n', '').replace(
        '₸', '')))
for key in soup.find_all('dt', class_="value-title"):
    keys.append(key.text.strip())
for value in soup.find_all('dd', class_="value"):
    values.append(value.text.strip())
keys.append("Описание")
values.append(soup.find('div', class_="offer__description").find('div', class_="text").find('p').getText().replace('\n',". "))
characteristics = dict(zip(keys, values))
print(characteristics)