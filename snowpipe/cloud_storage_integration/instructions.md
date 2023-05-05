This document provides instructions to configure secure access from Snowflake to the s3 bucket.
The process follows the Snowflake official documentation: https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto-s3

Step 1:
Create an IAM policy using AWS IAM service. (Copy and paste the content from SnowflakeIAMPolicy.json into the policy editor, make sure to set your bucket and prefix names.)

Step 2:
Create the IAM role using 'Another AWS account' as trusted entity, and enter your own AWS account ID as a temporary ID.
Select 'Require external ID' and pass a dummy temporarily. Then, allocate the policy created in Step 1 and create the role.

Step 3:
Create a Cloud Storage Integration in Snowflake by running csi.sql (remember to feed in your ARN from the role created in Step 2, as well as the bucket and prefix names)

Step 4:
Run 'DESC INTEGRATION <your_integration_name>;' in Snowflake to retrieve the Snowflake created 'STORAGE_AWS_IAM_USER_ARN' and 'STORAGE_AWS_EXTERNAL_ID'.

Step 5:
Go back to the role created in Step 2, select trust relationship -> edit trust relationship -> modify the policy here based on file SnowflakeTrustPolicy.json, make sure to change the values accordingly to your output from Step 4.

Your AWS Snowflake Storage Integration is created!
