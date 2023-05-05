# S&P500 Listed Stocks Historical Price Survivorship Bias Reduced Database
This project attempts to create a survivorship bias reduced database in Snowflake Cloud for S&P500 listed stock historical daily prices. The data pipeline consists of three parts:
    1. a WIKI web scraping process to obtain the S&P 500 listed stock symbols data
    2. an ETL process which runs in AWS Lambda serverless runtime environment for retrieving historical price data using the data from part 1.
    3. a Snowpipe for AWS S3 data extraction and a Change Data Capture (CDC) process to load our data into the final destination in Snowflake.

# Data Pipeline Overview
![image](https://user-images.githubusercontent.com/117455557/235351811-d7142884-5295-48de-8960-09c35f3775d7.png)

The pipeline and runtimes were designed to host on Cloud environments (AWS and Snowflake). This approach ensures a scalable and cost-effective solution for processing data in a timely manner.  

# S&P500 Listed Stock Symbols
The first part of the pipeline is to design a small database for storing historical S&P500 listings and tracking their changes. The data is stored in a semi-structured (json strings) method. This process is running as an AWS Lambda function and triggered via CloudWatch Event Schedules. The lambda function and its dependencies can be found in the folder "lambda_functions/snp500_ticker" within this repository.

## Extracting symbols
This Python script (get_symbols.py) creates a function which utilises the BeautifulSoup library to scrap table data from a Wikipedia page and retrieve a full list of S&P500 listed tickers/symbols at point in time. The function also allows filtering data based on specific criterias such as GICS sector, sub industries, etc. (We have applied filter on GICS defined Energy sector in this project as an example)

## Loading semi-structured ticker data into AWS S3
After receiving the list of symbols at point in time, the lambda function (write_symbols_lambda_function.py) compares the changes in the current list with last retrieved list and transform the data into a final output. The output also consists of data such as added/removed symbols at point in time. Finally, the data will be stored into an S3 location. This information will be used in subsequent parts of the data pipeline.

# S&P500 Historical Daily Price Data ETL process
The second part of the data pipeline extracts data via API calls and loads the cleaned up and structured data into another S3 location. This process was written in a Python script (lambda_functions/snp500_data/price_data_etl_lambda_function.py) and it was designed to be triggered by another AWS Lambda function via CloudWatch Event Schedules on a daily basis (pre-market opening times).

Using the data that we received in part 1 of the data pipeline, we are able to feed the payload information for extracting time-series daily price data from AlphaVantage RESTful API. Next, the data is transformed into a tabular format from json string format. Finally, the data is loaded into a AWS S3 bucket, waiting to be consumed by Snowflake via Snowpipe (part 3 of the data pipeline). By storing data in S3, we can also take advantage of AWS's features like versioning, access control, and lifecycle policies.

# Snowpipe and Snowflake CDC process
The third and final part of this pipeline is to load the data from AWS S3 into Snowflake via Snowpipe. By using Snowflake as our final data storage, we are able to make use of its powerful data warehousing capabilities and highly performant cloud solutions.

## Secure access to AWS S3
In the folder "snowpipe/cloud_storage_integration" within this repository, we have provided the instructions of creating a Snowflake user (Storage Integration) that could interact with our S3 bucket. The primary reason of using a storage integration is mentioned in Snowflake official documention - "Integrations are named, first-class Snowflake objects that avoid the need for passing explicit cloud provider credentials such as secret keys or access tokens".

## Snowpipe configuration
The SQL script "create_snowpipe.sql" demonstrated the process of creating a pipeline that allows auto ingesting. As a brief explanation, we first create a file format for csv files referencing. Next, an external stage was created to connect Snowflake with AWS S3 bucket using the csv referencing and storage integration we created earlier. Subsequently, we have created a pipe object to perform a COPY INTO command between the stage and a staging table, while this action will be triggerred based on Amazon Simple Queue Service (SQS) notifications referencing to our target path. In simple terms, we use an event notification to inform Snowpipe that the data is ready in S3 bucket.

## Change Data Capture (CDC) in Snowflake
Once the data being loaded into our staging table within Snowflake, a CDC process is performed in order to append the updated data into our original historical stock price table - this is documented in the script "append_original.sql". To achieve this process, we have configured a stream, a task tree and a stored procedure in our Snowflake environment. 

The stream is there to track any 'INSERT' operations within our staging table. Whenever an 'INSERT' action being detected, our parent task within the task tree will run a stored procedure that merges the new data from the staging table into the original table. Finally, 2 child tasks will be triggerred to clean up the stream and staging table.

# Requirements  
To run this project, you will need:

    AWS account with access to IAM, S3, EC2, Lambda
    Snowflake account with ACCOUNTADMIN role
    AlphaVantage API key
    Python 3.10
    Git

Install the required Python packages:

    pip install python-dotenv
    pip install requests
    pip install pandas
    pip install boto3
    pip install beautifulsoup4
    pip install regex

IMPORTANT! - Please note that these packages (apart from boto3) should also be installed on a Linux environment (can be done in a Linux Machine, AWS Cloud9 Linux EC2 Instance, Docker, etc.) and packaged into an AWS Lambda Layer to support your Lambda functions running without errors.
    
# Acknowledgments  
This project was originally developed by @teikkeat80 and @WilsonH918 as co-authors. Please feel free to suggest improvements and report any bugs.
