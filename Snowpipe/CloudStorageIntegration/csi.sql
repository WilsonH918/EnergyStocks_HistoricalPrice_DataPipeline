-- Generate IAM user for s3 cloud storage integration based on the root user ARN role created in AWS IAM Console.
CREATE STORAGE INTEGRATION s3_snowflake
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'Your ARN value'
    STORAGE_ALLOWED_LOCATIONS = ('Your s3 bucket path');
