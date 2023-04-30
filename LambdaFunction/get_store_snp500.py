class StockData:
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket_name = 'snp500-db'
        self.symbols_key = 'symbols.csv'

    def get_symbol(self, symbol):
        # Retrieve historical stock price data for a given stock symbol from AlphaVantage API

        url = 'https://www.alphavantage.co/query'
        api_key = os.getenv('AlphaVantage_API_KEY')

        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': api_key
        }

        response = requests.get(url, params=params)
        data = response.json()
        return data

    def store_symbol(self, symbol):
        # Store the historical stock price data for a given stock symbol in S3 data lake

        data = self.get_symbol(symbol)

        # Filter necessary columns and modify them before saving to S3
        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
        df = df.reset_index()
        df = df.rename(columns={'index': 'date', '1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adjusted_close', '6. volume': 'volume', '7. dividend amount': 'dividend_amount', '8. split coefficient': 'split_coefficient'})
        df['symbol'] = symbol

        # Save to S3
        s3_object = self.s3.Object(self.bucket_name, f'{symbol}.csv')
        s3_object.put(Body=df.to_csv(index=False))
