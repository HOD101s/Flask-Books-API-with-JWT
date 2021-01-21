import json
import boto3
import time

table_name = 'data'
with open("dynamoSetup/data.json", encoding="utf8") as f:
    json_data = json.load(f)

ddb_client = boto3.client("dynamodb", endpoint_url='http://localhost:8000')

response = ddb_client.create_table(
    AttributeDefinitions=[
        {
            'AttributeName': 'bookID',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },
    ],
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'bookID',
            'KeyType': 'HASH'
        }
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'title',
            'KeySchema': [
                {
                    'AttributeName': 'title',
                    'KeyType': 'HASH'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
    ],
    BillingMode='PAY_PER_REQUEST',
)

time.sleep(10)

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000').Table(table_name)
with ddb.batch_writer() as batch:
    for item in json_data:
        print(item)
        item['title'] = str(item['title'])
        batch.put_item(Item=item)
