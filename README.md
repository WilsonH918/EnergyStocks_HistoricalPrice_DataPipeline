# EnergyStocks HistoricalPrice DataPipeline  
This is a data pipeline project that retrieves S&P500 listed energy companies' historical stock price data, stores the data in an AWS S3 bucket, and transforms the data in a Snowflake data warehouse. The project is automated using AWS Lambda to trigger a Python script that runs the pipeline on a scheduled basis.

# Data Pipeline Overview  
![image](https://user-images.githubusercontent.com/117455557/235351811-d7142884-5295-48de-8960-09c35f3775d7.png)  

# Lambda Function  
The pipeline is designed to trigger the script via CloudWatch settings for Lambda, which then triggers an AWS EC2 instance to run the script whenever new data is available. This approach ensures a scalable and cost-effective solution for processing data in a timely manner.  

## get_store_snp500.py  
This Python script utilizes the BeautifulSoup library to extract data from Wikipedia and retrieve information about the S&P 500 companies. The script then filters the data based on specific criteria, and stores the results in an S3 data lake. By storing this information, we are able to use it in subsequent sessions to query financial data from AlphaVantage. This data serves as the foundation for creating our payload, which will be used to extract financial data from AlphaVantage.  

## energy_stocks_to_s3.py  
The "energy_stocks_to_s3.py" script is an essential component of our data pipeline that helps us efficiently store and retrieve financial data for analysis purpose. This script uses the AWS S3 to store and retrieve financial data related to the S&P 500 companies.  

To start, the script retrieves the S&P 500 tickers data from an S3 bucket that was previously created for this purpose. Once the data is extracted, the script filters the data based on specified criteria, such as the GICS sector, and creates a request payload to retrieve the financial data from the AlphaVantage RESTful API.  

After successfully retrieving the data, the script filters and modifies the necessary columns before saving the financial data in the S3 data lake. This approach allows for efficient storage and retrieval of data in a highly scalable and durable object store. By storing data in S3, we can take advantage of AWS's features like versioning, access control, and lifecycle policies.  

The financial data stored in AWS S3 is then used by Snowflake, our data warehousing solution, for further processing. Snowflake is a highly available and performant data cloud that provides powerful data warehousing solution.  

# Snowpipe  
The following part (Transform) of this pipeline is to store the stock price historical datasets in Snowflake via Snowpipe.

## Secure access to AWS S3
In the folder "Snowpipe/CloudStorageIntegration" within this repository, we have provided the instructions of creating a Snowflake user (Storage Integration) that could interact with our S3 bucket. The primary reason of using a storage integration is mentioned in Snowflake official documention - "Integrations are named, first-class Snowflake objects that avoid the need for passing explicit cloud provider credentials such as secret keys or access tokens".

## Snowpipe configuration
The SQL script "CreateSnowpipe.sql" demonstrated the process of creating a pipeline that allows auto ingesting. As a brief explanation, we first create a file format for csv files referencing. Next, an external stage was created to connect Snowflake with AWS S3 bucket using the csv referencing and storage integration we created earlier. Subsequently, we have created a pipe object to perform a COPY INTO command between the stage and a staging table, while this action will be triggerred based on Amazon Simple Queue Service (SQS) notifications referencing to our target path. In simple terms, we use an event notification to inform Snowpipe that the data is ready in S3 bucket.

## Change Data Capture (CDC) in Snowflake
Once the data being loaded into our staging table within Snowflake, a CDC process is performed in order to append the updated data into our original historical stock price table - this is documented in the script "AppendOriginal.sql". To achieve this process, we have configured a stream, a task tree and a stored procedure in our Snowflake environment. 

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
    
# Acknowledgments  
This script was developed by @teikkeat80 and @WilsonH918 as co-authors. Please feel free to suggest improvements and report any bugs.
