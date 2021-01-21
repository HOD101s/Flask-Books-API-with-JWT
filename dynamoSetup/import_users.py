import boto3
import uuid
import hashlib

ddb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")

ddb.create_table(
    TableName='datausers',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        }
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'username',
            'KeySchema': [
                {
                    'AttributeName': 'username',
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
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

dummyusers = [
    {
        'username': 'User1',
        'password': 'pass1'
    },
    {
        'username': 'User2',
        'password': 'pass2'
    }
]

with ddb.Table('datausers').batch_writer() as batch:
    for user in dummyusers:
        user['id'] = uuid.uuid4().hex
        user['password'] = hashlib.sha256(user['password'].encode('utf-8')).hexdigest()
        batch.put_item(Item=user)