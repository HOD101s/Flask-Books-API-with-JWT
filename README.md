# Flask API :

Made for ECS backend cloud developer test

## Setup

1. Run startDynamo.bat : starts local dynamodb
2. Run import_data.py and import_users.py from dynamo_db_schema to create required tables and import necessary data

## Usage Example

#### 1. Call login

Send username and password POST params. If no user created manually use :- username:User1 & password:pass1.
On successful login you will be issued an API token. This is valid for 15 minutes.

#### 3. Or use add_user endpoint to add user

```
http://127.0.0.1:5000/add_user?username=User3&password=pass3
```

#### 4. Call any endpoint

example 1:

```
url: http://127.0.0.1:5000/add_book/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlVzZXIxIiwiaWQiOiI0MWUzY2RmMzExYzQ0N2YzOWY3YjlkOGZiOGI4NGUyMiIsImV4cCI6MTYxMTIzNDgyNn0.dkbBqU7Azh8UkC9QTc-qjrnB-G6TJhlg6CKZ9MO07D0

with POST params
addtitle:dummyTitle
addauthor:leAuthor
addrating:123
addisbn:12321312
addlangcode:eng
addratingcount:123124
addprice:10
```

example 2:

```
http://127.0.0.1:5000/get_book/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlVzZXIxIiwiaWQiOiI0MWUzY2RmMzExYzQ0N2YzOWY3YjlkOGZiOGI4NGUyMiIsImV4cCI6MTYxMTIzODI4Mn0.BReOsvw0oqdDtT5z5WTLo1s0bzorR--ED_KsXaU8IPk?bookID=6
```

Refer [API Documentation](./API_documentation/readme.md) for API usage

## Testing

run :

```
python unit_test_cases/tests.py
```
