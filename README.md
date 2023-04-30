# EnergyStocks HistoricalPrice DataPipeline  
This is a data pipeline project that retrieves historical price data for energy stocks from the S&P 500 index, stores the data in an AWS S3 bucket, and transforms the data in a Snowflake data warehouse. The project is automated using AWS Lambda to trigger a Python script that runs the pipeline on a scheduled basis.

# Data Pipeline Overview  
![image](https://user-images.githubusercontent.com/117455557/235349895-7fe576e3-8ab9-48c2-b3b0-fe7714933b56.png)  

# Lambda Function  
The pipeline is designed to trigger the script via CloudWatch settings for Lambda, which then triggers an AWS EC2 instance to run the script whenever new data is available. This approach ensures a scalable and cost-effective solution for processing data in a timely manner.  

## get_store_snp500.py  
This Python script utilizes the BeautifulSoup library to extract data from Wikipedia and retrieve information about the S&P 500 companies. The script then filters the data based on specific criteria, and stores the results in an S3 data lake. By storing this historical S&P 500 data, we are able to use it in subsequent sessions to query financial data from AlphaVantage. This data serves as the foundation for creating our payload, which will be used to extract financial data from AlphaVantage.  

Once the data is extracted, the "energy_stocks_to_s3.py" script quickly filters and modifies the necessary columns before saving the data in an S3 data lake. This approach allows for efficient storage and retrieval of data in a highly scalable and durable object store. The data in AWS S3 is then used by Snowflake for further processing, providing a highly available and performant data warehouse solution for analysis and reporting.  

In summary, this Python script serves as a critical component of a robust data engineering pipeline designed for efficient processing and storage of historical stock price data for energy stocks in the S&P500. The script's use of modern cloud technologies ensures a scalable, cost-effective, and highly available solution for processing and analyzing data.  

# Snowpipe  


# Requirements  
To run this project, you will need:

    AWS account with access to S3, EC2, Lambda, and Snowflake
    Python 3.10
    Git

Install the required Python packages:

    pip install python-dotenv
    pip install requests
    pip install pandas
    pip install boto3
    pip install beautifulsoup4
    
# Acknowledgments  
This script was developed by @teikkeat80 and @WilsonH918 as coauthors. Please feel free to suggest improvements and report any bugs.
