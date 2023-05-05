from bs4 import BeautifulSoup
import requests
import pandas as pd

def get_symbols(filter=False, criteria=None, value=None):

    """Get a list of S&P500 symbols from Wikipedia based on a filter criteria (GICS Sector, Sub Sector etc.)

    Returns:
        list: a list of S&P 500 stock symbol based on your requirements
    """

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    table_id = 'constituents'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table_html = soup.find('table', attrs={'id' : table_id}) # S&P 500 companies table on Wiki
    df = pd.read_html(str(table_html))[0]

    if filter == True:
        df_filtered = df[df[criteria] == value]
        symbols = list(df_filtered['Symbol'])
    else:
        symbols = list(df['Symbol'])

    return symbols
