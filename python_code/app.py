import os
import uuid
import jwt
import hashlib
import boto3
import datetime
from flask_cors import CORS
from functools import wraps
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, request, jsonify

app = Flask(__name__)
cors = CORS(app)
app.config['SECRET_KEY'] = 'thisissecret'

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
usertable = ddb.Table('datausers')
bookstable = ddb.Table('data')


# for token authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'token' in kwargs:
            try:
                jwt.decode(kwargs['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
                return f(*args, **kwargs)
            except:
                return jsonify({'message': 'failed to authenticate request', 'error_code': 'invalid token'}), 300
        elif 'token' in request.cookies:
            try:
                jwt.decode(request.cookies.get('token'), app.config['SECRET_KEY'], algorithms=['HS256'])
                return f(*args, **kwargs)
            except:
                return jsonify({'message': 'failed to authenticate request', 'error_code': 'invalid token'}), 300
        else:
            return jsonify({'message': 'failed to authenticate request', 'error_code': 'invalid token'}), 300

    return decorated


@app.route('/checktoken/<string:token>', methods=['GET'])
@token_required
def checktoken(**kwargs):
    return jsonify({'message': 'token verified'}), 200


@app.route('/login', methods=['POST'])
def login():
    try:
        query = usertable.query(
            IndexName='username',
            KeyConditionExpression=Key('username').eq(request.form['username']),
            FilterExpression=Attr('password').eq(hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest())
        )
        if query["Items"]:
            token = jwt.encode({'username': request.form['username'], 'id': query["Items"][0]['id'],
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
                               app.config['SECRET_KEY'])
            return jsonify({'token': token, 'message': 'token generated'}), 200
        return jsonify({'message': 'failed to authenticate', 'error_code': 'Failed Auth'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/get_books/<string:token>', methods=['POST'])
@token_required
def get_books(**kwargs):
    try:
        # get book by title
        query = bookstable.query(
            IndexName='title',
            KeyConditionExpression=Key('title').eq(request.form['filtername'])
        )
        if query['Items']:
            # getting pagination
            page = request.form['start_page']
            size = request.form['page_size']

            if page == '' or page == '0':
                page = 1
            else:
                page = int(page)
            if size == '' or size == '0':
                size = 50
            else:
                size = int(size)
            first_index = size * (page - 1)
            return jsonify(query['Items'][first_index:first_index + size]), 200
        else:
            return jsonify({'message': 'No matches on filter', 'error_code': 'No Match'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/get_book/<string:token>', methods=['GET'])
@token_required
def get_book(**kwargs):
    try:
        # get book by ID
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.args.get('bookID'))
        )
        # check if response is not empty
        if query['Items']:
            return query['Items'][0], 200
        return jsonify({'message': 'No Matching Id', 'error_code': 'Book not found'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/add_book/<string:token>', methods=['POST'])
@token_required
def add_book(**kwargs):
    try:
        # build book info dict and add to bookstable
        bookstable.put_item(
            Item={
                "bookID": uuid.uuid4().hex,
                "title": request.form['addtitle'],
                "authors": request.form['addauthor'],
                "average_rating": request.form['addrating'],
                "isbn": request.form['addisbn'],
                "language_code": request.form['addlangcode'],
                "ratings_count": request.form['addratingcount'],
                "price": request.form['addprice']
            }
        )
        return jsonify({'message': 'added book'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/update_book/<string:token>', methods=['POST'])
@token_required
def update_book(**kwargs):
    try:
        # get book by ID
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.form['updatebookID'])
        )

        if not query['Items']:
            return jsonify({'message': 'No Matching Id', 'error_code': 'Book not found'}), 200

        # build update dict
        updatedict = {
            ":newtitle": request.form['uptitle'] if request.form['uptitle'] != '' else query['Items'][0]['title'],
            ":auth": request.form['upauthor'] if request.form['upauthor'] != '' else query['Items'][0]['authors'],
            ":rat": request.form['uprating'] if request.form['uprating'] != '' else query['Items'][0]['average_rating'],
            ":isbn": request.form['upisbn'] if request.form['upisbn'] != '' else query['Items'][0]['isbn'],
            ":lang": request.form['uplangcode'] if request.form['uplangcode'] != '' else query['Items'][0][
                'language_code'],
            ":ratcnt": request.form['upratingcount'] if request.form['upratingcount'] != ''
            else query['Items'][0]['ratings_count'],
            ":price": request.form['upprice'] if request.form['upprice'] != '' else query['Items'][0]['price']
        }

        # update item
        bookstable.update_item(
            Key={
                'bookID': request.form['updatebookID']
            },
            UpdateExpression='SET authors=:auth, average_rating=:rat, isbn=:isbn, language_code=:lang, price=:price, '
                             'ratings_count=:ratcnt, title=:newtitle',
            ExpressionAttributeValues=updatedict
        )

        return jsonify({'message': 'updated book'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


@app.route('/add_favourite/<string:token>', methods=['POST'])
@token_required
def add_favourite(**kwargs):
    try:
        # check if book exists
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.form['favbookID'])
        )
        # if exists continue
        if query['Items']:
            # decode token for user details
            data = jwt.decode(kwargs['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
            userdata = usertable.query(
                KeyConditionExpression=Key('id').eq(data['id'])
            )

            # if favourites exists update list else create attribute
            if 'favourites' not in userdata['Items'][0]:
                usertable.update_item(
                    Key={
                        'id': data['id'],
                    },
                    UpdateExpression='SET #attr1 = :val1',
                    ExpressionAttributeNames={'#attr1': 'favourites'},
                    ExpressionAttributeValues={':val1': [request.form['favbookID']]}
                )
            elif request.form['favbookID'] not in userdata['Items'][0]['favourites']:
                usertable.update_item(
                    Key={
                        'id': data['id'],
                    },
                    UpdateExpression='SET #attr1 = list_append(#attr1, :val1)',
                    ExpressionAttributeNames={'#attr1': 'favourites'},
                    ExpressionAttributeValues={':val1': [request.form['favbookID']]}
                )
            return jsonify({'message': 'added book to favourites'}), 200
        return jsonify({'message': 'failed to add book', 'error_code': 'Book not found'}), 200
    except:
        return jsonify({'message': 'failed to add book', 'error_code': 'failed to add book'}), 200


@app.route('/remove_favourite/<string:token>', methods=['POST'])
@token_required
def remove_favourite(**kwargs):
    try:
        # check if book exists
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(request.form['rembookID'])
        )

        if not query['Items']:
            return jsonify({'message': 'failed to remove book', 'error_code': 'Book Doesnt exist'}), 200

        # decode token for user details
        data = jwt.decode(kwargs['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
        userdata = usertable.query(
            KeyConditionExpression=Key('id').eq(data['id']),
        )
        # get item index
        index = userdata["Items"][0]['favourites'].index(request.form['rembookID'])

        if index is None:
            return jsonify({'message': 'failed to remove book', 'error_code': 'Book Doesnt exist in favourites'}), 200

        # remove item
        usertable.update_item(
            Key={
                'id': data['id'],
            },
            UpdateExpression=f'REMOVE favourites[{index}]',
        )
        return jsonify({'message': 'Removed book'}), 200
    except:
        return jsonify({'message': 'failed to remove book', 'error_code': 'failed to remove book'}), 200


@app.route('/get_favourite/<string:token>', methods=['GET'])
@token_required
def get_favourite(**kwargs):
    # decode token for user details
    data = jwt.decode(kwargs['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
    userdata = usertable.query(
        KeyConditionExpression=Key('id').eq(data['id'])
    )
    resp = []
    # if favourites doesnt exist
    if 'favourites' not in userdata['Items'][0]:
        return jsonify({'message': 'No favourites exists', 'error_code': 'Favourites is Empty'}), 200
    # build response
    for id in userdata['Items'][0]['favourites']:
        query = bookstable.query(
            KeyConditionExpression=Key('bookID').eq(id)
        )
        resp.append(query['Items'][0])
    return jsonify(resp), 200


@app.route('/add_user', methods=['GET'])
def add_user(**kwargs):
    try:
        usertable.put_item(
            Item={
                'id': uuid.uuid4().hex,
                'username': request.args.get('username'),
                'password': hashlib.sha256(request.args.get('password').encode('utf-8')).hexdigest()
            })
        return jsonify({'message': 'Added User'}), 200
    except:
        return jsonify({'message': 'failed to connect to db'}), 500


if __name__ == '__main__':
    app.run()
