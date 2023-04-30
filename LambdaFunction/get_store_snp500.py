import boto3
import pandas as pd
import requests
from bs4 import BeautifulSoup

class StockData:
    
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket_name = 'snp500-db'
        self.symbols_key = 'symbols.csv'

    def get_symbols(self, criteria, value):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table_id = 'constituents'

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        table_html = soup.find('table', attrs={'id' : table_id}) # S&P 500 companies table on Wiki
        df = pd.read_html(str(table_html))[0]

        df_filtered = df[df[criteria] == value]
        symbols = list(df_filtered['Symbol'])

        # Store the symbols in S3 for later reference
        symbols_df = pd.DataFrame(symbols, columns=['symbol'])
        s3_object = self.s3.Object(self.bucket_name, self.symbols_key)
        s3_object.put(Body=symbols_df.to_csv(index=False))

        return symbols
