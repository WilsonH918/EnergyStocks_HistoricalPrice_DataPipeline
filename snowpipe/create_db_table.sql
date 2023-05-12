-- Create Snowflake database for the project
CREATE OR REPLACE DATABASE FIN_PROJ;

-- Set DATABASE and SCHEMA
USE DATABASE FIN_PROJ;
USE SCHEMA PUBLIC;

-- Create original table
CREATE OR REPLACE TABLE snp500_price (
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
primary key ("date", symbol));
