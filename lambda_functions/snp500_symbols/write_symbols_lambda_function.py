from get_symbols import get_symbols
import json
import datetime
import boto3

# s3 setup
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'snp500-db'
    folder_path = 'ticker/'

    # Get latest json file in s3 folder
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    sorted_objects = sorted(objects['Contents'], key=lambda k: k['LastModified'], reverse=True)
    latest_json_file_key = next((obj['Key'] for obj in sorted_objects if obj['Key'].endswith('.json')), None)
    latest_json = json.loads(s3.get_object(Bucket=bucket_name, Key=latest_json_file_key)['Body'].read().decode('utf-8'))

    # Get ticker list
    current_list = get_symbols(filter=True, criteria='GICS Sector', value='Energy')

    # Get the current date
    current_date = datetime.date.today().strftime('%Y%m%d')

    # Get the latest data in json string
    latest_key = str(max([int(key) for d in latest_json for key in d.keys()]))

    latest_result = [d[latest_key] for d in latest_json if latest_key in d.keys()][0]

    # Update new ticker list
    latest_cum_symbols_list = latest_result['cum_symbols']

    current_set = set(current_list)
    prev_latest_set = set(latest_cum_symbols_list)

    added = list(current_set - (current_set & prev_latest_set))
    dropped = list(prev_latest_set - (current_set & prev_latest_set))
    cum_symbols = list(current_set | prev_latest_set)

    current_dict = {
        current_date: {
            'symbols': current_list,
            'cum_symbols': cum_symbols,
            'added': added,
            'dropped': dropped
        }
    }

    if latest_key == current_date:
        raise Exception("Today's data has already been updated")

    updated_data = latest_json + [current_dict]
    updated_json_string_bytes = bytes(json.dumps(updated_data).encode('utf-8'))

    # Upload to s3
    file_key = f'{folder_path}snp500lot_{current_date}.json'

    s3.put_object(Body=updated_json_string_bytes, Bucket=bucket_name, Key=file_key)

    print(f'Successfully uploaded {file_key} to {bucket_name}!')