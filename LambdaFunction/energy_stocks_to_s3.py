import os
from dotenv import load_dotenv
import requests
import pandas as pd
import re
import boto3
from datetime import date
import time
import datetime
from bs4 import BeautifulSoup


class EnergyStocksToS3:
    
    def __init__(self):
        load_dotenv()
        self.symbols = self.get_symbols('GICS Sector', 'Energy')
        self.csv_file_path = '/tmp/energy_stocks.csv'
        self.bucket_name = 'snp500-db'
    
    def get_symbols(self, criteria, value):
        # Get a list of S&P500 symbols from Wikipedia based on a filter criteria (GICS Sector, Sub Sector etc.)
        # Returns a list of S&P 500 stock symbol based on your requirements

        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table_id = 'constituents'

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        table_html = soup.find('table', attrs={'id': table_id})  # S&P 500 companies table on Wiki
        df = pd.read_html(str(table_html))[0]

        df_filtered = df[df[criteria] == value]
        symbols = list(df_filtered['Symbol'])

        # Store the symbols in S3 for later reference
        symbols_df = pd.DataFrame(symbols, columns=['symbol'])
        s3_object = self.s3.Object(self.bucket_name, self.symbols_key)
        s3_object.put(Body=symbols_df.to_csv(index=False))

        return symbols
        
    def run(self, event, context):
        # Get the stocks daily adjusted price data from Alpha Vantage
        json_data_list = []
        for symbol in self.symbols:
            self.params['symbol'] = symbol
            response = requests.get(self.url, params=self.params)
            json_data = response.json()
            json_data_list.append(json_data)
            time.sleep(13)
            
        # Parse the json data and put into dataframe
        df = pd.DataFrame()
        for item in json_data_list:
            symbol_metadata = item['Meta Data']['2. Symbol']
            data = item['Time Series (Daily)']
            df_temp = pd.DataFrame.from_dict(data, orient='index')
            df_temp['symbol'] = symbol_metadata
            df = pd.concat([df, df_temp])

        # Cleaning the columns
        parsed_columns = [re.sub(r'^\d+\.\s*', '', col, 1) for col in df.columns]
        df.columns = parsed_columns
        df.index = pd.to_datetime(df.index)
        df.columns = df.columns.str.replace(' ', '_')

        # Filter only recent 10 years data
        df_filtered = df[df.index.year >= date.today().year - 10]

        # Get Date as a column
        df_filtered = df_filtered.reset_index().rename(columns={'index': 'date'})

        # Load data to csv file
        df_filtered.to_csv(self.csv_file_path, index=False)

        # Set up Boto3 client for S3
        s3 = boto3.client('s3', aws_access_key_id = os.getenv('Access_key_ID'), aws_secret_access_key = os.getenv('secret_access_key'))

        # Define the S3 file key to store the data
        sysdate = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_key = f'snowflake/energy_stocks_{sysdate}.csv'

        # Upload the file to S3
        with open(self.csv_file_path, 'rb') as f:
            s3.upload_fileobj(f, self.bucket_name, file_key)

        print(f'Successfully uploaded {file_key} to {self.bucket_name}!')
