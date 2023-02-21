#make query with link from parser
import pandas as pd

from parser.ParserKolesa import ParserKolesa

link = input()
parser = ParserKolesa()
data = parser.queryWithTheLink(link)
df = pd.DataFrame([data])
#save as excel
df.to_excel('cars.xlsx', index=False)
