/*
This sql script demonstreates the creation of a Snowpipe 
or auto data ingestion process.
Follow the below steps to create the Snowpipe.
*/

-- Step 0:
-- Generate IAM user for s3 cloud storage integration based on the root user ARN role created in AWS IAM Console.
CREATE STORAGE INTEGRATION s3_snowflake
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::413508458176:role/snowflake_role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://snp500-db/snowflake/');
-- Please continue with 'DESC STORAGE INTEGRATION s3_snowflake' to obtain the Snowflake generated ARN.

-- Set DATABASE and SCHEMA
USE DATABASE FIN_PROJ;
USE SCHEMA PUBLIC;

-- Step 1:
-- Create staging table, for data pre-load
CREATE OR REPLACE TABLE snp500_price_stagetable (
    "date" date,
    open float,
    high float,
    low float,
    close float,
    adjusted_close float,
    volume integer,
    dividend_amount double,
    split_coefficient double,
    symbol string,
    primary key ("date", symbol)
);

-- Step 2:
-- Create a CSV file format for file type references in following steps
CREATE OR REPLACE FILE FORMAT s3_snowpipe_csv 
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE;

-- Step 3:
-- Create an S3 external stage with IAM user defined earlier (Step 1)
CREATE OR REPLACE STAGE s3_snowpipe_stage
    URL = 's3://snp500-db/snowflake/'
    STORAGE_INTEGRATION = s3_snowflake
    FILE_FORMAT = s3_snowpipe_csv;

-- Step 4:
-- Create a Snowpipe for Auto Ingestion based on SQS Event Notifications from S3 Bucket
CREATE OR REPLACE PIPE s3_snowpipe 
    AUTO_INGEST = TRUE as
      COPY INTO snp500_price_stagetable
      FROM @public.s3_snowpipe_stage
      FILE_FORMAT = s3_snowpipe_csv;
