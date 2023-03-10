# class for Parser Kolesa class
import json
import time
import random

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt


class ParserKolesa:
    def __init__(self):
        super().__init__()
        # url of site
        self.df = None
        self.url = 'https://kolesa.kz/cars/'
        # list of links to cars
        self.links = []
        # list of cars
        self.cars = []
        # headers for requests
        self.headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.2.261 Yowser/2.5 Safari/537.36'
        }

    def generate_url(self):
        location = input('Enter location: ')
        location = location + "/" if location != '' else location
        brand = input('Enter brand: ')
        brand = brand + "/" if brand != '' else brand
        model = input('Enter model: ')
        model = model + "/" if model != '' else model

        url = self.url + brand + model + location
        extras = input('Enter extras: ')
        extras = "/?" + extras if extras != '' else extras
        self.url = url + extras

    def query(self, input):
        temp_url = self.url
        temp_url = temp_url + input[0] + '/' + input[1] + '/' + input[4] + '/?'
        temp_url = temp_url + 'year[from]=' + input[2] + '&year[to]=' + input[2]
        self.url = temp_url
        self.get_links()
        self.parse_cars()
        self.saveToMongo()
        return self.cars

    def queryWithTheLink(self, link):
        self.url = link
        self.get_links()
        self.parse_cars()
        self.saveToMongo()
        return self.cars

    def get_links(self):
        # get all href values where class="a-card__link"
        temp_url = self.url
        print(temp_url)
        request = requests.get(temp_url, headers=self.headers)
        soup = BeautifulSoup(request.content, 'html.parser')
        for link in soup.find_all('a', class_="a-card__link"):
            self.links.append("https://kolesa.kz/" + link.get('href'))
        #append all unique links to self.links
        self.links = list(set(self.links))

    def parse_cars(self):
        cars = []
        print(self.links)
        for link in self.links:
            # catch error if we have no access to the link and continue
            try:
                request = requests.get(link, headers=self.headers, timeout=5)
            except:
                print(667)
                continue
            soup = BeautifulSoup(request.content, 'html.parser')
            # get all values in a dictionary
            keys = []
            values = []
            keys.append("brand")
            values.append(soup.find('span', itemprop="brand").text.strip())
            keys.append("model")
            values.append(soup.find('span', itemprop="name").text.strip())
            keys.append("year")
            values.append(int(soup.find('span', class_="year").text.strip()))
            keys.append("price")
            values.append(
                int(soup.find('div', class_="offer__price").text.strip().replace('\xa0', '').replace('\n', '').replace(
                    '???', '')))
            for key in soup.find_all('dt', class_="value-title"):
                keys.append(key.text.strip())
            for value in soup.find_all('dd', class_="value"):
                temp = value.text.strip() if value.text.strip() != '??????' else False
                temp = temp if temp != '????' else True
                values.append(temp)
                # if we have ket with name '??????????' we will replace it with 'city'
                if '??????????' in keys:
                    keys[keys.index('??????????')] = 'city'
                # if we have ket with name '????????????' we will replace it with 'mileage'
                if '????????????' in keys:
                    keys[keys.index('????????????')] = 'mileage'
                # if we have ket with name '?????? ????????????' we will replace it with 'body_type'
                if '??????????????????' in keys:
                    keys[keys.index('??????????????????')] = 'generation'
                if '??????????' in keys:
                    keys[keys.index('??????????')] = 'body_type'
                if '?????????? ??????????????????, ??' in keys:
                    keys[keys.index('?????????? ??????????????????, ??')] = 'engine_volume'
                if '?????????????? ??????????????' in keys:
                    keys[keys.index('?????????????? ??????????????')] = 'transmission'
                if '????????????' in keys:
                    keys[keys.index('????????????')] = 'drive'
                if '????????' in keys:
                    keys[keys.index('????????')] = 'steering_wheel'
                if '????????????' in keys:
                    keys[keys.index('????????????')] = 'drive'
                if '????????' in keys:
                    keys[keys.index('????????')] = 'color'
                if '???????????????????? ?? ????????????????????' in keys:
                    keys[keys.index('???????????????????? ?? ????????????????????')] = 'custom_cleared'
            characteristics = dict(zip(keys, values))
            cars.append(characteristics)
            keys.append("description")
            # make if this will bring error to append empty string
            try:
                values.append(soup.find('div', class_="offer__description").find('div', class_="text").find(
                    'p').getText().replace('\n', ". "))
            except:
                values.append('')

        self.cars = cars



    def saveToMongo(self):
        print(self.cars)
        self.df = pd.DataFrame(self.cars)
        df = self.df
        print('Done')
        client = MongoClient("mongodb://localhost:27017/")
        db = client["endterm"]
        collection = db["cars"]
        self.cars = json.loads(json.dumps(self.cars))
        print(self.cars)
        collection.insert_many(self.cars)

    def outWithExcel(self):
        self.df = pd.DataFrame(self.cars)
        df = self.df
        df.to_excel('cars.xlsx')
        print('Done')

    def run(self):
        self.get_links()
        self.parse_cars()
        self.saveToMongo()

    def run_with_visualization(self):
        self.get_links()
        self.parse_cars()
        self.out()
        self.visualize()

    def visualize(self):
        # import all data from mongodb to pandas dataframe and visualize it
        client = MongoClient("mongodb://localhost:27017/")
        db = client["endterm"]
        collection = db["cars"]
        # aggregate by city with average price
        pipeline = [
            {"$group": {"_id": "$brand", "average_price": {"$avg": "$price"}}}
        ]
        result = collection.aggregate(pipeline)
        result = list(result)
        df = pd.DataFrame(result)
        df.plot.bar(x='_id', y='average_price')
        plt.show()

    def getAveragePrice(self):
        temp_cars = self.cars
        # get average price of all cars
        sum = 0
        for car in temp_cars:
            sum += car['price']
        return sum / len(temp_cars)
