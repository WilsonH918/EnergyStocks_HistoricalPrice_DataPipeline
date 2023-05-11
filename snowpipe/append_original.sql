/*
This sql script demonstrates the use of Snowflake Stream, Tasks, and Stored
Prodecure to update the original data table based on Change Data Capture (CDC)
process. Please follow the steps below to create the pipeline.

Pre-requisites:
1. staging table
2. original table

Note: This process is an extension for the process built in snowpipe.sql,
which enabled us to create a CDC workflow and efficiently manage the original table.
*/

-- Step 1:
-- Create a 'MERGE INTO' Stored Procedure that inserts new rows into the original table based on the differences in rows between staging and original table.
CREATE OR REPLACE PROCEDURE snp500_price_merge_procedure()
    RETURNS STRING
    LANGUAGE SQL
    AS
    $$
    BEGIN
      MERGE INTO fin_proj.public.snp500_price t
      USING fin_proj.public.snp500_price_stagetable s
      ON t.symbol = s.symbol AND t."date" = s."date"
    
      WHEN NOT MATCHED THEN INSERT(
        symbol, "date", open, high, low, close, adjusted_close, volume, dividend_amount, split_coefficient
      ) VALUES (
        s.symbol, s."date", s.open, s.high, s.low, s.close, s.adjusted_close, s.volume, s.dividend_amount, s.split_coefficient
      );
      
      RETURN 'Upload completed and staging table cleared';
      
    END;
    $$
;

-- Step 2:
-- Create a stream to track the INSERT DML action within the stage table, i.e., whenever the table is performed with INSERT action, SYSTEM$STREAM_HAS_DATA returns TRUE
CREATE OR REPLACE STREAM snp500_price_stream 
    ON TABLE snp500_price_stagetable 
    APPEND_ONLY = TRUE;

-- Step 3:
-- Create a Snowflake Task DAG to call the Stored Procedure and perform resources cleaning actions.

-- Step 3.0.1 (parent): Calling the stored procedure based on SYSTEM$STREAM_HAS_DATA is TRUE
CREATE OR REPLACE TASK snp500_price_merge_task
    WAREHOUSE = 'COMPUTE_WH'
    SCHEDULE = 'USING CRON * * * * * America/New_York'
WHEN 
    SYSTEM$STREAM_HAS_DATA('snp500_price_stream') 
    AS CALL snp500_price_merge_procedure();

-- Step 3.0.2: Clean up values in stage table
CREATE OR REPLACE TASK snp500_price_clearstage_task
    WAREHOUSE = 'COMPUTE_WH'
    AFTER snp500_price_merge_task
    AS DELETE FROM fin_proj.public.snp500_price_stagetable;

-- Step 3.0.3: Consume Stream Data and do nothing, revert SYSTEM$STREAM_HAS_DATA back to FALSE
CREATE OR REPLACE TASK snp500_price_clearstream_task
    WAREHOUSE = 'COMPUTE_WH'
    AFTER snp500_price_clearstage_task
    AS CREATE OR REPLACE TEMP TABLE fin_proj.public.reset_table AS SELECT * FROM fin_proj.public.snp500_price_stream;

-- Step 3.5:
-- Resume 1st task (parent task) due to initial suspension

ALTER TASK snp500_price_merge_task RESUME;
