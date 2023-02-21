#get data from mongodb db name endterm collection name cars and convert it to pandas dataframe

#download the data from the mongodb database
import pymongo
import pandas as pd
import numpy as np
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["endterm"]
mycol = mydb["cars"]
mylist = list(mycol.find())
df = pd.DataFrame(mylist)
df = df.drop(columns=['_id'])
#drop all the rows which are duplicates
df = df.drop_duplicates()
df.head()
#print size of the data
print(df.shape)
#input the data to the csv file
df.to_csv('cars.csv', index=False)