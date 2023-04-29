# EnergyStocks_HistoricalPrice_DataPipeline  
This is a data pipeline project that retrieves historical price data for energy stocks from the S&P 500 index, stores the data in an AWS S3 bucket, and transforms the data in a Snowflake data warehouse. The project is automated using AWS Lambda to trigger a Python script that runs the pipeline on a scheduled basis.

# Requirements  
To run this project, you will need:  
AWS account with access to S3, EC2, Lambda, and Snowflake  
Python 3.x and pip  
Git  

Installation

    Clone this repository:

    bash

git clone https://github.com/WilsonH918/EnergyStocks_HistoricalPrice_DataPipeline.git

Install the required Python packages:

bash

pip install -r requirements.txt

Create a virtual environment (optional but recommended):

bash

    python -m venv env
    source env/bin/activate

    Create an AWS S3 bucket to store the data and update the config.json file with your bucket name.

    Create a Snowflake data warehouse and update the config.json file with your Snowflake credentials.

    Create an AWS Lambda function to trigger the pipeline script and configure it to run on a scheduled basis. Update the config.json file with your Lambda function name and schedule.

    Update the get_symbols.py file with your S&P 500 API key.

Usage

To run the pipeline manually, run the following command:

bash

python energy_stocks_to_s3.py

To run the pipeline automatically on a scheduled basis, configure the AWS Lambda function to trigger the energy_stocks_to_s3.py script at your desired schedule.
