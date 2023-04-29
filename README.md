# EnergyStocks_HistoricalPrice_DataPipeline  
This is a data pipeline project that retrieves historical price data for energy stocks from the S&P 500 index, stores the data in an AWS S3 bucket, and transforms the data in a Snowflake data warehouse. The project is automated using AWS Lambda to trigger a Python script that runs the pipeline on a scheduled basis.

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
