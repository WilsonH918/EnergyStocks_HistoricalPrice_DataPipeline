# EnergyStocks_HistoricalPrice_DataPipeline  
This is a data pipeline project that retrieves historical price data for energy stocks from the S&P 500 index, stores the data in an AWS S3 bucket, and transforms the data in a Snowflake data warehouse. The project is automated using AWS Lambda to trigger a Python script that runs the pipeline on a scheduled basis.

# Data Pipeline Overview  
![image](https://user-images.githubusercontent.com/117455557/235311127-b62d48fd-a53a-4934-9ac1-87d561ffa5a5.png)

# Lambda Function
The pipeline is designed to trigger the script via CloudWatch settings for Lambda, which then triggers an AWS EC2 instance to run the script whenever new data is available. This approach ensures a scalable and cost-effective solution for processing data in a timely manner.  

Once the data is extracted, the "energy_stocks_to_s3.py" script quickly filters and modifies the necessary columns before saving the data in an S3 data lake. This approach allows for efficient storage and retrieval of data in a highly scalable and durable object store. The data in AWS S3 is then used by Snowflake for further processing, providing a highly available and performant data warehouse solution for analysis and reporting.  

In summary, this Python script serves as a critical component of a robust data engineering pipeline designed for efficient processing and storage of historical stock price data for energy stocks in the S&P500. The script's use of modern cloud technologies ensures a scalable, cost-effective, and highly available solution for processing and analyzing data.  


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
