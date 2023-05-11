import os
from dotenv import load_dotenv
import requests
import pandas as pd
import re
import datetime
import time
import boto3
import json

# Load dotenv
load_dotenv()

# s3 setup
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # s3 location definitions
    bucket_name = 'snp500-db'
    ticker_folder_path = 'ticker/'
    snowflake_folder_path = 'snowflake/'

    # Get latest json file in s3 folder
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=ticker_folder_path)
    sorted_objects = sorted(objects['Contents'], key=lambda k: k['LastModified'], reverse=True)
    latest_json_file_key = next((obj['Key'] for obj in sorted_objects if obj['Key'].endswith('.json')), None)
    latest_json_ticker = json.loads(s3.get_object(Bucket=bucket_name, Key=latest_json_file_key)['Body'].read().decode('utf-8'))

    # Get the latest data in json string
    latest_key_ticker = str(max([int(key) for d in latest_json_ticker for key in d.keys()]))
    latest_result_ticker = [d[latest_key_ticker] for d in latest_json_ticker if latest_key_ticker in d.keys()][0]

    # Get a list of stock symbols
    symbols = latest_result_ticker['cum_symbols']

    # Get the stocks daily adjusted price data from Alpha Vantage
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': None,                                                             # Initial value
        'outputsize': 'full',
        'apikey': os.getenv('AlphaVantage_API_KEY')
    }

    json_data_list = []
    for symbol in symbols:
        params['symbol'] = symbol
        response = requests.get(url, params=params)
        json_data = response.json()
        json_data_list.append(json_data)
        time.sleep(13)                                                              # Limit less than 5 API calls per minute

    # Parse the json data and put into dataframe
    df = pd.DataFrame()
    for item in json_data_list:
        symbol_metadata = item['Meta Data']['2. Symbol']
        data = item['Time Series (Daily)']
        df_temp = pd.DataFrame.from_dict(data, orient='index')
        df_temp['symbol'] = symbol_metadata
        df = pd.concat([df, df_temp])

    # Cleaning the columns
    parsed_columns = [re.sub(r'^\d+\.\s*', '', col, 1) for col in df.columns]       # Remove the numerical bullet points
    df.columns = parsed_columns
    df.index = pd.to_datetime(df.index)
    df.columns = df.columns.str.replace(' ', '_')

    # Filter only recent 10 years data
    df_filtered = df[df.index.year >= datetime.date.today().year - 10]

    # Get Date as a column
    df_filtered = df_filtered.reset_index().rename(columns={'index': 'date'})

    # Load data to temp location in csv format
    temp_file_path = '/tmp/file_temp.csv'
    df_filtered.to_csv(temp_file_path, index=False)

    # Get current date
    current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Upload to s3
    file_key = f'{snowflake_folder_path}snp500_{current_datetime}.csv'

    with open(temp_file_path, 'rb') as f:
        s3.upload_fileobj(f, bucket_name, file_key)

    print('Successfully uploaded!')
