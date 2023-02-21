# load xg_reg model
import pickle
import numpy as np
import re
import pandas as pd

from parser.ParserKolesa import ParserKolesa

model = pickle.load(open('ML/AP_project/model.pkl', 'rb'))


def dfCheck(df):
    # load dictionary for each column from json file
    # if mileage is nan I want to replace it with the 10000*(2023-year)
    df['mileage'] = df['mileage'].fillna(10000 * (2023 - df['year'].astype(int)))
    # if color is nan I want to replace it with the "не указан"
    df['color'] = df['color'].fillna("не указан")
    df['Наличие'] = df['Наличие'].fillna(True)
    df['Наличие'] = df['Наличие'].replace('На заказ', False)
    isPetrol = []
    for i in range(len(df)):
        if df.engine_volume[i] == 'газ-бензин':
            isPetrol.append(False)
        else:
            isPetrol.append(True)
    df['isPetrol'] = isPetrol
    # delete all signs in engine_volume except numbers
    engine_volume = []
    for i in range(len(df)):
        a = df.engine_volume[i]
        engine_volume.append(re.sub('[^\d\.]', '', a))
    df['engine_volume'] = engine_volume
    mileage = []
    for i in range(len(df)):
        a = str(df.mileage[i])
        mileage.append(re.sub('[^\d\.]', '', a))

    mileage = [int(float(i)) for i in mileage]
    df['mileage'] = mileage
    if 'VIN' in df.columns:
        df = df.drop(columns=['VIN'])
    df["engine_volume"] = df["engine_volume"].astype(float)
    return df


if __name__ == '__main__':
    # make input of ['brand', 'model', 'year', 'price', 'city', 'generation', 'body_type','engine_volume',
    # 'transmission', 'drive', 'steering_wheel','custom_cleared', 'mileage', 'color', 'Наличие', 'isPetrol'] if input
    # equals -1, then it will be replaced by NaN
    parser = ParserKolesa()
    columns = ['brand', 'model', 'year', 'price', 'city', 'generation', 'body_type', 'engine_volume', 'transmission',
               'drive',
               'steering_wheel', 'custom_cleared', 'mileage', 'color', 'Наличие', 'isPetrol']
    categorical_columns = ['brand', 'model', 'city', 'generation', 'body_type', 'transmission', 'drive',
                           'steering_wheel', 'color']
    # link = input("please enter link:")
    # data = parser.queryWithTheLink(link)
    data1 = []
    for i in range(len(columns)):
        data1.append(input("please enter " + columns[i] + ":"))
        # replace -1 with NaN
    for i in range(16):
        if data1[i] == '-1':
            data1[i] = np.nan
    # check if input is in dictionary, if not, then add new key-value pair

    # get the first row of data
    # concatenate data to dataframe
    data = pd.DataFrame([data1], columns=columns)
    data = dfCheck(data)
    # divide data to X and y
    X = data.drop(columns=['price'])
    y = data['price']
    # fit X and y
    X = pd.get_dummies(X, columns=categorical_columns)
    model.fit(X, y)
    X = data.drop(columns=['price'])
    y = data['price']
    # predict price
    print(model.predict(X))
