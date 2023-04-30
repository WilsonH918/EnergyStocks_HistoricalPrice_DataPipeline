import os
from dotenv import load_dotenv
import pandas as pd
import re
import boto3
from datetime import date
import time
import datetime


class EnergyStocksToS3:
    
    def __init__(self):
        load_dotenv()
        self.bucket_name = 'snp500-db'
        self.symbols_key = 'symbols/energy_symbols.csv'
        self.csv_file_path = '/tmp/energy_stocks.csv'
        self.symbols = self.get_symbols('GICS Sector', 'Energy')
        self.s3 = boto3.resource('s3', aws_access_key_id=os.getenv('Access_key_ID'),
                                 aws_secret_access_key=os.getenv('secret_access_key'))
    
    def get_symbols(self, criteria, value):
        # Get a list of S&P500 symbols from S3 bucket based on a filter criteria (GICS Sector, Sub Sector etc.)
        # Returns a list of S&P 500 stock symbol based on your requirements

        s3_object = self.s3.Object(self.bucket_name, self.symbols_key)
        symbols_df = pd.read_csv(s3_object.get()['Body'], dtype=str)
        df_filtered = symbols_df[symbols_df[criteria] == value]
        symbols = list(df_filtered['symbol'])
        return symbols
        
    def run(self, event, context):
        # Get the stocks daily adjusted price data from Alpha Vantage
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'outputsize': 'full',
            'datatype': 'json',
            'apikey': os.getenv('alpha_vantage_key')
        }

        json_data_list = []
        for symbol in self.symbols:
            params['symbol'] = symbol
            response = requests.get(url, params=params)
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

        # Define the S3 file key to store the data
        sysdate = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_key = f'snowflake/energy_stocks_{sysdate}.csv'

        # Upload the file to S3
        with open(self.csv_file_path, 'rb') as f:
            self.s3.Bucket(self.bucket_name).put_object(Key=file_key, Body=f)

        print(f'Successfully uploaded {file_key} to {self.bucket_name}!')
